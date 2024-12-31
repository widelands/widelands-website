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
import urllib.request, urllib.parse, urllib.error
import bleach

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

try:
    _domain = Site.objects.get(pk=settings.SITE_ID).domain
except:
    _domain = ""

# Getting local domain lists
try:
    LOCAL_DOMAINS = [_domain] + settings.LOCAL_DOMAINS
except ImportError:
    LOCAL_DOMAINS = [_domain]


register = template.Library()


def _insert_smileys(text):
    """This searches for smiley symbols in the current text and replaces them
    with the correct images.

    Contents get splitted into words and after this the whole contents must be
    reassembled.
    """

    tmp_content = []
    for content in text.parent.contents:
        try:
            # If this fails, content is probably '\n' or not a string, e.g.  <br />
            words = content.split(" ")
        except:
            # apply the unsplittable content and continue
            tmp_content.append(content)
            continue

        for i, word in enumerate(words):
            smiley = ""
            for sc, img in settings.SMILEYS:
                if word == sc:
                    smiley = img
            if smiley:
                img_tag = BeautifulSoup(features="lxml").new_tag("img")
                img_tag["src"] = "{}{}".format(settings.SMILEY_DIR, smiley)
                img_tag["alt"] = smiley
                tmp_content.append(img_tag)
                # apply a space after the smiley
                tmp_content.append(NavigableString(" "))
            else:
                if i < (len(words) - 1):
                    # Apply a space after each word, except the last word
                    word = word + " "
                tmp_content.append(NavigableString(word))

    text.parent.contents = tmp_content


def _classify_link(tag):
    """Applies a classname if this link is in any way special
    (external or missing wikipages)

    tag: classify for this tag

    """

    # No class change for image links
    if tag.next_element and tag.next_element.name == "img":
        return

    try:
        href = tag["href"].lower()
        if not tag.string:
            # Apply href to empty linkname, e.g.: [](/some/link)
            # Just to be sure tag.next_element is never None
            tag.string = href
    except KeyError:
        return

    # Check for external link
    if href.startswith("http"):
        for domain in LOCAL_DOMAINS:
            external = True
            if href.find(domain) != -1:
                external = False
                break
        if external:
            tag["class"] = "externalLink"
            tag["title"] = "This link refers to outer space"
            tag["target"] = "_blank"
            return

    if "/profile/" in (tag["href"]):
        tag["class"] = "userLink"
        tag["title"] = "This link refers to a userpage"
        return

    if check_for_missing_wikipages and href.startswith("/wiki/"):
        # Check for missing wikilink /wiki/PageName[/additionl/stuff]
        # Using href because we need cAsEs here
        article_name = urllib.parse.unquote(tag["href"][6:].split("/", 1)[0])

        if not len(article_name):  # Wiki root link is not a page
            tag["class"] = "wrongLink"
            tag["title"] = "This Link misses an articlename"
            return

        # Wiki special pages are also not counted
        if article_name in settings.WIKI_SPECIAL_PAGES:
            tag["class"] = "specialLink"
            return

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
                return
            else:
                return
        except IndexError:
            pass

        # article missing (or misspelled)
        if Article.objects.filter(title=article_name).count() == 0:
            tag["class"] = "missingLink"
            tag["title"] = (
                "This Link is misspelled or missing. Click to create it anyway."
            )
            return
    return


def _make_clickable_images(tag):
    # is external link?
    if tag["src"].startswith("http"):
        # Do not change if it is already a link
        if tag.parent.name != "a":
            # add link to image
            new_link = BeautifulSoup(features="lxml").new_tag("a")
            new_link["href"] = tag["src"]
            new_img = BeautifulSoup(features="lxml").new_tag("img")
            new_img["src"] = tag["src"]
            try:
                new_img["alt"] = tag["alt"]
            except KeyError:
                pass
            new_link.append(new_img)
            tag.replace_with(new_link)
    return


def find_smiley_Strings(bs4_string):
    """Find strings that contain a smiley symbol.

    Don't find a smiley in code tags.
    Attention: This returns also True for ':/' in 'http://'. This get
    fixed in _insert_smileys().
    """

    if bs4_string.parent.name.lower() == "code":
        return False

    for sc in settings.SMILEYS:
        if sc[0] in bs4_string:
            return True
    return False


# Predefine the markdown extensions here to have a clean code in
# do_wl_markdown()
md_extensions = ["extra", "toc", "mdx_wikilink_plus"]
md_configs = {
    "mdx_wikilink_plus": {"base_url": "/wiki/", "url_whitespace": "%20"},
}


def do_wl_markdown(value, *args, **keyw):
    """Apply wl specific things, like smileys or colored links."""

    beautify = keyw.pop("beautify", True)
    html = markdown(value, extensions=md_extensions, extension_configs=md_configs)

    # Sanitize posts from potencial untrusted users (Forum/Wiki/Maps)
    if "bleachit" in args:
        html = mark_safe(
            bleach.clean(
                html,
                tags=settings.BLEACH_ALLOWED_TAGS,
                attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
            )
        )

    # Prepare the html and apply smileys and classes.
    # BeautifulSoup objects are all references, so changing a variable
    # derived from the soup will take effect on the soup itself.
    # Because of that the called functions will modify the soup directly.
    soup = BeautifulSoup(html, features="lxml")
    if len(soup.contents) == 0:
        # well, empty soup. Return it
        return str(soup)

    if beautify:
        # Insert smileys
        smiley_text = soup.find_all(string=find_smiley_Strings)
        for text in smiley_text:
            _insert_smileys(text)

        # Classify links
        for tag in soup.find_all("a"):
            _classify_link(tag)

        # All external images gets clickable
        # This applies only in forum
        for tag in soup.find_all("img"):
            _make_clickable_images(tag)
    return "".join([str(x) for x in soup.body.children])


@register.filter
def wl_markdown(content, arg=""):
    """A Filter which decides when to 'bleach' the content."""
    if arg == "bleachit":
        return mark_safe(do_wl_markdown(content, "bleachit"))
    else:
        return mark_safe(do_wl_markdown(content))
