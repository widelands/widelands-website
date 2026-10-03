#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: mainpage/templatetags/wl_markdown.py
#
# Created by Holger Rapp on 2009-02-27.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from markdown import markdown
import nh3
import re
import urllib.request, urllib.parse, urllib.error

from bs4 import BeautifulSoup, NavigableString

# If we can import a Wiki module with Articles, we
# will check for internal wikipages links in all internal
# links starting with /wiki/
try:
    from wiki.models import Article, ChangeSet

    check_for_missing_wikipages = True
except ImportError:
    check_for_missing_wikipages = False

# We will also need the site domain
from django.contrib.sites.models import Site


def _get_domains():
    # Converted to a function to fix APPS_NOT_READY_WARNING_MSG in Django 5.2
    # Every database query should be in a function or Class…
    try:
        _domain = Site.objects.get(pk=settings.SITE_ID).domain
    except Site.DoesNotExist:
        _domain = ""
    # Getting local domain lists
    try:
        local_domains = [_domain] + settings.LOCAL_DOMAINS
    except:
        locaL_domains = [_domain]
    return local_domains


register = template.Library()


def _make_smileys(text):
    """This searches for smiley symbols in the current text and replaces them
    with the correct images.
    """

    new_soup = BeautifulSoup()
    words = text.split()
    preceding_space = text.startswith(" ")
    smileys = settings.SMILEYS

    for count, word in enumerate(words):
        found_smiley = False

        for i, _ in enumerate(smileys):
            if word == smileys[i][0]:
                found_smiley = smileys[i]

        if found_smiley:
            img_tag = new_soup.new_tag("img")
            img_tag["src"] = f"{settings.SMILEY_DIR}{found_smiley[1]}"
            img_tag["alt"] = found_smiley[0]
            new_soup.append(img_tag)
            # apply a space after the smiley
            new_soup.append(NavigableString(" "))
        else:
            if preceding_space:
                word = " " + word
                preceding_space = False

            if count < (len(words) - 1):
                # Apply a space after each word, except the last word
                word = word + " "
            new_soup.append(NavigableString(word))

    return new_soup


def _classify_link(tag):
    """Applies a classname if this link is in any way special
    (external or missing wikipages)

    tag: classify for this tag

    """

    # No class change for image links
    if tag.next_element and tag.next_element.name == "img":
        return None

    try:
        href = tag["href"].lower()
        if not tag.string:
            # Apply href to empty linkname, e.g.: [](/some/link)
            # Just to be sure tag.next_element is never None
            tag.string = href
    except KeyError:
        return None

    # Check for external link
    if href.startswith("http"):
        external = False
        for domain in _get_domains():
            external = True
            if href.find(domain) != -1:
                external = False
                break
        if external:
            tag["class"] = "externalLink"
            tag["title"] = "This link refers to outer space"
            tag["target"] = "_blank"
            return tag

    if "/profile/" in (tag["href"]):
        tag["class"] = "userLink"
        tag["title"] = "This link refers to a userpage"
        return tag

    if check_for_missing_wikipages and href.startswith("/wiki/"):
        # Check for missing wikilink /wiki/PageName[/additionl/stuff]
        # Using href because we need cAsEs here
        article_name = urllib.parse.unquote(tag["href"][6:].split("/", 1)[0])

        if not len(article_name):  # Wiki root link is not a page
            tag["class"] = "wrongLink"
            tag["title"] = "This Link misses an articlename"
            return tag

        # Wiki special pages are also not counted
        if article_name in settings.WIKI_SPECIAL_PAGES:
            tag["class"] = "specialLink"
            return tag

        # Check for a redirect
        try:
            # try to get the article id; if this fails an IndexError is raised
            a_id = ChangeSet.objects.filter(old_title=article_name).values_list(
                "article_id"
            )[0]

            # get actual title of article
            act_t = Article.objects.get(id=a_id[0]).title
            if article_name != act_t:
                tag["title"] = 'This is a redirect and points to "' + act_t + '"'
                return tag
            else:
                return None
        except IndexError:
            pass

        # article missing (or misspelled)
        if Article.objects.filter(title=article_name).count() == 0:
            tag["class"] = "missingLink"
            tag["title"] = (
                "This Link is misspelled or missing. Click to create it anyway."
            )
            return tag
    return None


def _make_clickable_images(tag, rel=None):
    # is external link?
    if tag["src"].startswith("http"):
        # Do not change if it is already a link
        if tag.parent.name != "a":
            # add link to image
            new_link = BeautifulSoup(features="lxml").new_tag("a")
            new_link["href"] = tag["src"]
            if rel:
                new_link["rel"] = rel
            new_img = BeautifulSoup(features="lxml").new_tag("img")
            new_img["src"] = tag["src"]
            try:
                new_img["alt"] = tag["alt"]
            except KeyError:
                pass
            new_link.append(new_img)
            return new_link
    return None


def find_smiley_strings(bs4_string):
    """Find strings that contain a smiley symbol.

    Don't find a smiley in code tags.
    Attention: This returns also True for ':/' in 'http://'. This get
    fixed in _insert_smileys().
    """
    if bs4_string.parent.name.lower() == "code":
        return False

    for sc, _ in settings.SMILEYS:
        if sc in bs4_string:
            return True
    return False


# Predefine the markdown extensions here to have a clean code in
# do_wl_markdown()
md_extensions = ["extra", "toc", "tables", "mdx_wikilink_plus"]
md_configs = {
    "mdx_wikilink_plus": {"base_url": "/wiki/", "url_whitespace": "%20"},
    "tables": {"use_align_attribute": "True"},
}

# The start of a tag ("<name" or "</name") as the HTML parser tokenizes it
_TAG_START = re.compile(r"<(/?)([A-Za-z][^\s/>]*)")

# Links in user content get no ranking credit from search engines.
USER_CONTENT_LINK_REL = "nofollow ugc"


def _sanitize(html):
    """Remove all tags, attributes and URL schemes that are not allowed in the
    settings, and mark all links with USER_CONTENT_LINK_REL.

    nh3 drops disallowed tags, but users often write placeholders like
    '<username>' or types like 'vector<int>' outside of code blocks. To show
    them as text, the '<' starting a disallowed tag is escaped first. nh3
    sanitizes the result, so this pre-pass only turns markup into text and
    is not needed for safety.
    """
    allowed_tags = set(settings.SANITIZER_ALLOWED_TAGS)
    html = _TAG_START.sub(
        lambda m: m[0] if m[2].lower() in allowed_tags else f"&lt;{m[1]}{m[2]}",
        html,
    )
    return nh3.clean(
        html,
        tags=allowed_tags,
        attributes={
            tag: set(attributes)
            for tag, attributes in settings.SANITIZER_ALLOWED_ATTRIBUTES.items()
        },
        url_schemes=set(settings.SANITIZER_ALLOWED_URL_SCHEMES),
        link_rel=USER_CONTENT_LINK_REL,
    )


def do_wl_markdown(value, *, sanitize=False, beautify=True):
    """Apply wl specific things, like smileys or colored links.

    sanitize: set for content from untrusted users (forum, wiki, maps,
    comments): removes disallowed HTML and marks links as user content.
    """
    html = markdown(value, extensions=md_extensions, extension_configs=md_configs)

    if sanitize:
        html = _sanitize(html)

    # Prepare the html and apply smileys and classes.
    soup = BeautifulSoup(html, features="lxml")
    if len(soup.contents) == 0:
        # well, empty soup. Return it
        return str(soup)

    if beautify:
        # Insert smileys
        smiley_text = soup.find_all(string=find_smiley_strings)
        for text in smiley_text:
            # Remove content and apply the new one
            text.replace_with(_make_smileys(text))

        # Classify links
        for tag in soup.find_all("a"):
            new_tag = _classify_link(tag)
            if new_tag:
                tag.replace_with(new_tag)

        # All external images gets clickable
        # This applies only in forum
        for tag in soup.find_all("img"):
            new_tag = _make_clickable_images(
                tag, rel=USER_CONTENT_LINK_REL if sanitize else None
            )
            if new_tag:
                tag.replace_with(new_tag)

    # Remove <html><body> tags inserted by lxml. decode_contents() escapes
    # text nodes, whereas str() of a NavigableString would not.
    return soup.body.decode_contents()


@register.filter
def wl_markdown(content, arg=""):
    """Render markdown; use wl_markdown:"sanitize" for untrusted content."""
    if arg not in ("", "sanitize"):
        # A typo must not silently skip the sanitizer.
        raise ValueError(f'wl_markdown: unknown argument "{arg}"')
    return mark_safe(do_wl_markdown(content, sanitize=arg == "sanitize"))
