import os.path
import random
import traceback
import json
import re
import subprocess

from bs4 import BeautifulSoup, NavigableString
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.functional import Promise
from django.utils.translation import check_for_language
from django.utils.encoding import force_text
from django import forms
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.conf import settings
from django.core.exceptions import ValidationError
from pybb import settings as pybb_settings
import magic
import zipfile
import configparser
from PIL import Image


def allowed_for(user):
    """Check if a user has the permission to enter internal Forums."""

    return user.is_superuser or user.has_perm(pybb_settings.INTERNAL_PERM)


def render_to(template_path):
    """Expect the dict from view.

    Render returned dict with RequestContext.

    """

    def decorator(func):
        def wrapper(request, *args, **kwargs):
            import pdb

            # output = pdb.runcall(func, request, *args, **kwargs)
            output = func(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output

            # TODO(Franku): 'MIME_TYPE' is never in output as i can see for now.
            # But if, this should maybe 'content_type' instead
            if "MIME_TYPE" in output:
                kwargs["mimetype"] = output.pop("MIME_TYPE")
            if "TEMPLATE" in output:
                template = output.pop("TEMPLATE")
            else:
                template = template_path

            return render(request, template, output)

        return wrapper

    return decorator


def ajax(func):
    """Checks request.method is POST. Return error in JSON in other case.

    If view returned dict, returns JsonResponse with this dict as
    content.

    """

    def wrapper(request, *args, **kwargs):
        if request.method == "POST":
            try:
                response = func(request, *args, **kwargs)
            except Exception as ex:
                response = {"error": traceback.format_exc()}
        else:
            response = {"error": {"type": 403, "message": "Accepts only POST request"}}
        if isinstance(response, dict):
            return JsonResponse(response)
        else:
            return response

    return wrapper


class LazyJSONEncoder(json.JSONEncoder):
    """This fing need to save django from crashing."""

    def default(self, o):
        if isinstance(o, Promise):
            return force_text(o)
        else:
            return super(LazyJSONEncoder, self).default(o)


class JsonResponse(HttpResponse):
    """HttpResponse subclass that serialize data into JSON format."""

    # TODO(Franku): The mimetype argument maybe must be replaced with content_type

    def __init__(self, data, mimetype="application/json"):
        json_data = LazyJSONEncoder().encode(data)
        super(JsonResponse, self).__init__(content=json_data, content_type=mimetype)


def build_form(Form, _request, GET=False, *args, **kwargs):
    """Shorcut for building the form instance of given form class."""

    if not GET and "POST" == _request.method:
        form = Form(_request.POST, _request.FILES, *args, **kwargs)
    elif GET and "GET" == _request.method:
        form = Form(_request.GET, _request.FILES, *args, **kwargs)
    else:
        form = Form(*args, **kwargs)
    return form


PLAIN_LINK_RE = re.compile(r"(http[s]?:\/\/[-a-zA-Z0-9@:%._\+~#=/?]+)")


def exclude_code_tag(bs4_string):
    if bs4_string.parent.name == "code":
        return False
    m = PLAIN_LINK_RE.search(bs4_string)
    if m:
        return True
    return False


def urlize(data):
    """Urlize plain text links in the HTML contents.

    Do not urlize content of A and CODE tags.

    """

    soup = BeautifulSoup(data, "lxml")
    for found_string in soup.find_all(string=exclude_code_tag):
        new_content = []
        strings_or_tags = found_string.parent.contents
        for string_or_tag in strings_or_tags:
            try:
                for string in PLAIN_LINK_RE.split(string_or_tag):
                    if string.startswith("http"):
                        # Apply an a-Tag
                        tag = soup.new_tag("a")
                        tag["href"] = string
                        tag.string = string
                        tag["nofollow"] = "true"
                        new_content.append(tag)
                    else:
                        # This is just a string, apply a bs4-string
                        new_content.append(NavigableString(string))
            except:
                # Regex failed, so apply what ever it is
                new_content.append(string_or_tag)

        # Apply the new content
        found_string.parent.contents = new_content

    return str(soup)


def quote_text(text, user, markup):
    """Quote message using selected markup."""

    quoted_username = (
        settings.DELETED_USERNAME if user.wlprofile.deleted else user.username
    )

    text = "*" + quoted_username + " wrote:*\n\n" + text

    if markup == "markdown":
        # Inserting a space after ">" will not change the generated HTML,
        # but it will unbreak certain constructs like '>:-))'.
        return "> " + text.replace("\r", "").replace("\n", "\n> ") + "\n"
    elif markup == "bbcode":
        return "[quote]\n%s\n[/quote]\n" % text
    else:
        return text


def unescape(text):
    """Do reverse escaping."""

    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    return text


def validate_file(attachment):
    tmp_file_path = attachment.temporary_file_path()

    # Helper functions
    def _split_mime(mime_type):
        main, sub = mime_type.split("/", maxsplit=1)
        return {"maintype": main, "subtype": sub}

    def _is_image():
        # Use PIL to determine if it is a valid image file
        # works not for corrupted jpg
        try:
            with Image.open(tmp_file_path) as im:
                im.verify()
        except:
            return False
        return True

    def _is_zip():
        try:
            zip_obj = zipfile.ZipFile(tmp_file_path)
        except zipfile.BadZipfile:
            return None
        return zip_obj

    def _zip_contains(zip_parts):
        # Check if each entry in zip_parts is inside the attachment
        zip_obj = _is_zip()
        if zip_obj:
            try:
                for obj in zip_parts:
                    zip_obj.getinfo(obj)
            except KeyError:
                return False
        return True

    # Main part of file checks
    # File size
    if attachment.size > pybb_settings.ATTACHMENT_SIZE_LIMIT:
        raise ValidationError(
            "Attachment is too big. We allow max %(size)s MiB",
            params={
                "size": pybb_settings.ATTACHMENT_SIZE_LIMIT / 1024 / 1024,
            },
        )

    # Checks by file extension
    splitted_fn = attachment.name.rsplit(".", maxsplit=2)
    if len(splitted_fn) == 1:
        raise ValidationError("We do not allow uploading files without an extension.")

    ext = splitted_fn[-1]
    if not ext in settings.ALLOWED_EXTENSIONS:
        raise ValidationError("This type of file is not allowed.")

    # Widelands map file
    if ext == "wmf":
        raise ValidationError(
            "This seems to be a widelands map file. Please upload \
            it at our maps section."
        )

    # Widelands savegame (*.wgf) and widelands replay (*.wrpl.wgf)
    # are not the same.
    if ext == "wgf" and not splitted_fn[-2] == "wrpl":
        if not _zip_contains(settings.WGF_CONTENT_CHECK):
            raise ValidationError("This is not a valid widelands savegame.")

    # Widelands replay
    if ext == "wrpl":
        raise ValidationError(
            "This file is part of a replay. Please zip it together with \
            the corresponding .wrpl.wgf file and upload again."
        )

    if ext == "zip":
        if _is_zip() == None:
            raise ValidationError("This is not a valid zip file.")

    # Widelands AI configuration
    if ext == "wai":
        wai = configparser.ConfigParser()
        try:
            wai.read(tmp_file_path)
            wai_sections = wai.sections()
            if len(settings.ALLOWED_WAI_SECTIONS) == len(wai_sections):
                for section in settings.ALLOWED_WAI_SECTIONS:
                    if section not in wai_sections:
                        raise
            else:
                raise
        except:
            raise ValidationError("This not a valid wai file.")

    # Checks by MimeType
    # Get MIME-Type from python-magic
    magic_mime = magic.from_file(tmp_file_path, mime=True)
    magic_mime = _split_mime(magic_mime)
    send_mime = _split_mime(attachment.content_type)

    # Check for valid image file. Use te mime-type provided by python-magic,
    # because for a renamed image the wrong mime-type is send by the browser.
    if magic_mime["maintype"] == "image":
        if not _is_image():
            raise ValidationError(
                "This is not a valid image: %(file)s", params={"file": attachment.name}
            )

    # Compare Mime type send by browser and Mime type from python-magic.
    # We only compare the main type (the first part) because the second
    # part may not be recoginzed correctly. E.g. for .lua the submitted
    # type is 'text/x-lua' but 'x-lua' is not official at all. See:
    # https://www.iana.org/assignments/media-types/media-types.xhtml
    # Unrecoginzed extension are always send with mime type
    # 'application/octet-stream'. Skip if we know them.
    if not ext in settings.SKIP_MIME_EXTENSIONS:
        if not magic_mime["maintype"] == send_mime["maintype"]:
            raise ValidationError(
                "The file %(file)s looks like %(send_mime)s, \
                but we think it is %(magic_mime)s",
                params={
                    "file": attachment.name,
                    "send_mime": send_mime["maintype"],
                    "magic_mime": magic_mime["maintype"],
                },
            )
