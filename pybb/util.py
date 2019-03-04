import os.path
import random
import traceback
import json
import re

from bs4 import BeautifulSoup, NavigableString
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.functional import Promise
from django.utils.translation import check_for_language
from django.utils.encoding import force_unicode
from django import forms
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.conf import settings
from pybb import settings as pybb_settings


def render_to(template_path):
    """Expect the dict from view.

    Render returned dict with RequestContext.

    """

    def decorator(func):
        def wrapper(request, *args, **kwargs):
            import pdb
            #output = pdb.runcall(func, request, *args, **kwargs)
            output = func(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            

            # TODO(Franku): 'MIME_TYPE' is never in output as i can see for now.
            # But if, this should maybe 'content_type' instead
            if 'MIME_TYPE' in output:
                kwargs['mimetype'] = output.pop('MIME_TYPE')
            if 'TEMPLATE' in output:
                template = output.pop('TEMPLATE')
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
        if request.method == 'POST':
            try:
                response = func(request, *args, **kwargs)
            except Exception, ex:
                response = {'error': traceback.format_exc()}
        else:
            response = {'error': {'type': 403,
                                  'message': 'Accepts only POST request'}}
        if isinstance(response, dict):
            return JsonResponse(response)
        else:
            return response
    return wrapper


class LazyJSONEncoder(json.JSONEncoder):
    """This fing need to save django from crashing."""

    def default(self, o):
        if isinstance(o, Promise):
            return force_unicode(o)
        else:
            return super(LazyJSONEncoder, self).default(o)


class JsonResponse(HttpResponse):
    """HttpResponse subclass that serialize data into JSON format."""
    # TODO(Franku): The mimetype argument maybe must be replaced with content_type

    def __init__(self, data, mimetype='application/json'):
        json_data = LazyJSONEncoder().encode(data)
        super(JsonResponse, self).__init__(
            content=json_data, content_type=mimetype)


def build_form(Form, _request, GET=False, *args, **kwargs):
    """Shorcut for building the form instance of given form class."""

    if not GET and 'POST' == _request.method:
        form = Form(_request.POST, _request.FILES, *args, **kwargs)
    elif GET and 'GET' == _request.method:
        form = Form(_request.GET, _request.FILES, *args, **kwargs)
    else:
        form = Form(*args, **kwargs)
    return form


PLAIN_LINK_RE = re.compile(r'(http[s]?:\/\/[-a-zA-Z0-9@:%._\+~#=/?]+)')
def exclude_code_tag(bs4_string):
    if bs4_string.parent.name == 'code':
        return False
    m = PLAIN_LINK_RE.search(bs4_string)
    if m:
        return True
    return False


def urlize(data):
    """Urlize plain text links in the HTML contents.

    Do not urlize content of A and CODE tags.

    """

    soup = BeautifulSoup(data, 'lxml')
    for found_string in soup.find_all(string=exclude_code_tag):
        new_content = []
        strings_or_tags = found_string.parent.contents
        for string_or_tag in strings_or_tags:
            try:
                for string in PLAIN_LINK_RE.split(string_or_tag):
                    if string.startswith('http'):
                        # Apply an a-Tag
                        tag = soup.new_tag('a')
                        tag['href'] = string
                        tag.string = string
                        tag['nofollow'] = 'true'
                        new_content.append(tag)
                    else:
                        # This is just a string, apply a bs4-string
                        new_content.append(NavigableString(string))
            except:
                # Regex failed, so apply what ever it is
                new_content.append(string_or_tag)

        # Apply the new content
        found_string.parent.contents = new_content

    return unicode(soup)


def quote_text(text, user, markup):
    """Quote message using selected markup."""

    quoted_username = settings.DELETED_USERNAME if user.wlprofile.deleted else user.username

    text = '*' + quoted_username + ' wrote:*\n\n' + text

    if markup == 'markdown':
        # Inserting a space after ">" will not change the generated HTML,
        # but it will unbreak certain constructs like '>:-))'.
        return '> ' + text.replace('\r', '').replace('\n', '\n> ') + '\n'
    elif markup == 'bbcode':
        return '[quote]\n%s\n[/quote]\n' % text
    else:
        return text


def unescape(text):
    """Do reverse escaping."""

    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', '\'')
    return text
