# -*- coding: utf-8 -*-

from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from django.http import (
    Http404,
    HttpResponseNotAllowed,
    HttpResponse,
    HttpResponseForbidden,
)
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.contrib.redirects.models import Redirect
from django.contrib.sites.shortcuts import get_current_site

from wiki.forms import ArticleForm
from wiki.models import Article, ChangeSet, dmp

from wiki.utils import get_ct
from django.contrib.auth.decorators import login_required
from mainpage.templatetags.wl_markdown import do_wl_markdown

from mainpage.wl_utils import get_valid_cache_key, get_pagination

from tagging.models import Tag

import re
import urllib.request, urllib.parse, urllib.error

# Settings
#  lock duration in minutes
try:
    WIKI_LOCK_DURATION = settings.WIKI_LOCK_DURATION
except AttributeError:
    WIKI_LOCK_DURATION = 15

try:
    from notification import models as notification
except ImportError:
    notification = None

# default querysets
ALL_ARTICLES = Article.objects.all()
ALL_CHANGES = ChangeSet.objects.all()
OFFICIAL_CHANGES = ChangeSet.official.all()


def get_redirect(article):
    try:
        return Redirect.objects.get(old_path=article.get_absolute_url())
    except Redirect.DoesNotExist:
        return None


def get_articles_by_group(
    article_qs, group_slug=None, group_slug_field=None, group_qs=None
):
    group = None
    if group_slug is not None:
        group = get_object_or_404(group_qs, **{group_slug_field: group_slug})
        article_qs = article_qs.filter(content_type=get_ct(group), object_id=group.id)
    return article_qs, group


def get_articles_for_object(object, article_qs=None):
    if article_qs is None:
        article_qs = ALL_ARTICLES
    return article_qs.filter(content_type=get_ct(object), object_id=object.id)


def get_url(urlname, group=None, args=None, kw=None):
    if group is None:
        return reverse(urlname, args=args)
    else:
        app = group._meta.app_label
        urlconf = ".".join([app, "urls"])
        url = reverse(urlname, urlconf, kwargs=kw)
        return "".join(["/", app, url])  # @@@ harcoded: /app/.../


class ArticleEditLock(object):
    """A soft lock to edting an article."""

    def __init__(self, title, request, message_template=None):
        self.title = title
        self.user = request.user
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if message_template is None:
            message_template = (
                "Possible edit conflict:"
                " Another user started editing this article at %s"
            )

        self.message_template = message_template
        cache.set(title, self, WIKI_LOCK_DURATION * 60)

    def create_message(self, request):
        """Show a message to the user if there is another user editing this
        article."""
        if not self.is_mine(request):
            messages.add_message(
                request, messages.INFO, self.message_template % self.created_at
            )

    def is_mine(self, request):
        return self.user == request.user


def has_read_perm(user, group, is_member, is_private):
    """Return True if the user has permission to *read*
    Articles, False otherwise.
    """
    if (group is None) or (is_member is None) or is_member(user, group):
        return True
    if (is_private is not None) and is_private(group):
        return False
    return True


def has_write_perm(user, group, is_member):
    """Return True if the user have permission to edit Articles, False
    otherwise."""
    if (group is None) or (is_member is None) or is_member(user, group):
        return True
    return False


def article_list(
    request,
    group_slug=None,
    group_slug_field=None,
    group_qs=None,
    article_qs=ALL_ARTICLES,
    ArticleClass=Article,
    template_name="index.html",
    template_dir="wiki",
    extra_context=None,
    is_member=None,
    is_private=None,
    *args,
    **kw,
):
    if request.method == "GET":
        articles, group = get_articles_by_group(
            article_qs, group_slug, group_slug_field, group_qs
        )

        allow_read = has_read_perm(request.user, group, is_member, is_private)
        allow_write = has_write_perm(request.user, group, is_member)

        if not allow_read:
            return HttpResponseForbidden()

        articles = articles.exclude(deleted=True).order_by("title")

        template_params = {"articles": articles, "allow_write": allow_write}

        if group_slug is not None:
            template_params["group"] = group
            new_article = ArticleClass(
                title="NewArticle", content_type=get_ct(group), object_id=group.id
            )
        else:
            new_article = ArticleClass(title="NewArticle")
        template_params["new_article"] = new_article
        if extra_context is not None:
            template_params.update(extra_context)

        return render(
            request,
            "/".join([template_dir, template_name]),
            template_params,
        )
    return HttpResponseNotAllowed(["GET"])


def view_article(
    request,
    title,
    revision=None,
    ArticleClass=Article,  # to create an unsaved instance
    group_slug=None,
    group_slug_field=None,
    group_qs=None,
    article_qs=ALL_ARTICLES,
    template_name="view.html",
    template_dir="wiki",
    extra_context=None,
    is_member=None,
    is_private=None,
    *args,
    **kw,
):
    if request.method == "GET":
        article_args = {"title": title}

        if article_args["title"] in settings.FORBIDDEN_WIKI_TITLES:
            raise Http404()

        if group_slug is not None:
            group = get_object_or_404(group_qs, **{group_slug_field: group_slug})
            article_args.update({"content_type": get_ct(group), "object_id": group.id})
            allow_read = has_read_perm(request.user, group, is_member, is_private)
            allow_write = has_write_perm(request.user, group, is_member)
        else:
            allow_read = allow_write = True

        if not allow_read:
            return HttpResponseForbidden()

        is_observing = False
        redirected_from = None
        try:
            article = article_qs.get(**article_args)
            if notification is not None:
                is_observing = notification.is_observing(article, request.user)
        except ArticleClass.DoesNotExist:
            try:
                # try to find an article that once had this title
                article = (
                    ChangeSet.objects.filter(old_title=title)
                    .order_by("-revision")[0]
                    .article
                )
                redirected_from = title
                # if article is not None:
                #    return redirect(article, permanent=True)
            except IndexError:
                article = ArticleClass(**article_args)

        if revision is not None:
            changeset = get_object_or_404(article.changeset_set, revision=revision)
            article.content = changeset.get_content()

        if article.deleted:
            if get_redirect(article):
                # A redirect is applied
                # The django Redirects app takes care for redirecting
                raise Http404()
            else:
                # This article was deleted and has no redirect
                return render(
                    request, "wiki/gone.html", context={"article": article}, status=410
                )

        template_params = {}
        outdated = False
        tags = [x.name for x in Tag.objects.get_for_object(article)]
        if "outdated" in tags:
            template_params.update({"outdated": True})

        template_params.update(
            {
                "article": article,
                "revision": revision,
                "redirected_from": redirected_from,
                "allow_write": allow_write,
            }
        )

        if notification is not None:
            template_params.update({"is_observing": is_observing, "can_observe": True})

        if group_slug is not None:
            template_params["group"] = group
        if extra_context is not None:
            template_params.update(extra_context)

        # If this articles name is an old name of the article,
        # apply the correct Http status
        http_status = 200
        if redirected_from:
            http_status = 301
        return render(
            request,
            "/".join([template_dir, template_name]),
            template_params,
            status=http_status,
        )
    return HttpResponseNotAllowed(["GET"])


@login_required
def edit_article(
    request,
    title,
    group_slug=None,
    group_slug_field=None,
    group_qs=None,
    article_qs=ALL_ARTICLES,
    ArticleClass=Article,  # to get the DoesNotExist exception
    ArticleFormClass=ArticleForm,
    template_name="edit.html",
    template_dir="wiki",
    extra_context=None,
    check_membership=False,
    is_member=None,
    is_private=None,
    *args,
    **kw,
):
    group = None
    article_args = {"title": title}
    if group_slug is not None:
        group = get_object_or_404(group_qs, **{group_slug_field: group_slug})
        group_ct = get_ct(group)
        article_args.update({"content_type": group_ct, "object_id": group.id})
        allow_read = has_read_perm(request.user, group, is_member, is_private)
        allow_write = has_write_perm(request.user, group, is_member)
    else:
        allow_read = allow_write = True

    if not allow_write:
        return HttpResponseForbidden()

    try:
        # Try to fetch an existing article
        article = article_qs.get(**article_args)
    except ArticleClass.DoesNotExist:
        # No article found, maybe we have a redirect
        try:
            cs = ChangeSet.objects.filter(old_title=title)[0]
            article = article_qs.get(title=cs.article)
        except IndexError:
            # No Article found and no redirect found
            article = None

    if request.method == "POST":
        form = ArticleFormClass(request.POST, instance=article)

        form.cache_old_content()
        if form.is_valid():
            if request.user.is_authenticated:
                form.editor = request.user

            if (article is None) and (group_slug is not None):
                form.group = group

            new_article, changeset = form.save()

            lock = cache.get(get_valid_cache_key(title))
            if lock is not None:
                # Clean the lock
                cache.delete(get_valid_cache_key(title))

            redirect_to = form.cleaned_data["redirect_to"]
            if redirect_to != "":
                # Create or update the redirect
                obj, created = Redirect.objects.update_or_create(
                    site=get_current_site(request),
                    old_path=new_article.get_absolute_url(),
                    defaults={"new_path": redirect_to},
                )
            else:
                # Remove redirect
                r = get_redirect(new_article)
                if r:
                    r.delete()

            if new_article.deleted and new_article.tags:
                # Remove all tags
                del new_article.tags
                new_article.save(update_fields=["tags"])

            if notification and not changeset.reverted:
                # Get observers for this article and exclude current editor
                items = (
                    notification.ObservedItem.objects.all_for(new_article, "post_save")
                    .exclude(user=request.user)
                    .iterator()
                )
                users = [o.user for o in items]

                if new_article.deleted:
                    # This will be the last notification
                    comment = (
                        "This Article was deleted and your observation was removed."
                    )
                    r = get_redirect(new_article)
                    if r:
                        path = r.new_path
                        if not path.startswith("http"):
                            path = (
                                f"{request.scheme}://{get_current_site(request)}{path}"
                            )
                        comment = f"{comment}\nWe made a redirect and the new content can be found at {path}"
                else:
                    comment = changeset.comment

                notification.send(
                    users,
                    "wiki_observed_article_changed",
                    {
                        "editor": request.user,
                        "rev": changeset.revision,
                        "rev_comment": comment,
                        "article": new_article,
                    },
                )
                if new_article.deleted:
                    # Remove observers
                    observers = notification.ObservedItem.objects.all_for(
                        new_article, "post_save"
                    )
                    for o in observers:
                        notification.stop_observing(new_article, o.user)

            return redirect(new_article)

    elif request.method == "GET":
        if (
            article
            and article.deleted
            and "/trash/" not in request.path_info  # for new articles
        ):
            return render(
                request, "wiki/gone.html", context={"article": article}, status=410
            )

        lock = cache.get(get_valid_cache_key(title))
        if lock is None:
            lock = ArticleEditLock(get_valid_cache_key(title), request)
        lock.create_message(request)
        initial = {}
        if group_slug is not None:
            initial.update({"content_type": group_ct.id, "object_id": group.id})

        if article is None:
            initial.update({"title": title, "action": "create"})
            form = ArticleFormClass(initial=initial)
        else:
            initial["action"] = "edit"
            r = get_redirect(article)
            if r:
                initial.update({"redirect_to": r.new_path})

            form = ArticleFormClass(instance=article, initial=initial)
    if not article:
        template_params = {"form": form, "new_article": True}
    else:
        template_params = {
            "form": form,
            "new_article": False,
            "content_type": ContentType.objects.get_for_model(Article).pk,
            "object_id": article.pk,
            "images": article.all_images(),
            "article": article,
        }

    if group_slug is not None:
        template_params["group"] = group
    if extra_context is not None:
        template_params.update(extra_context)

    return render(
        request,
        "/".join([template_dir, template_name]),
        template_params,
    )


def view_changeset(
    request,
    title,
    revision,
    revision_from=None,
    group_slug=None,
    group_slug_field=None,
    group_qs=None,
    article_qs=ALL_ARTICLES,
    changes_qs=ALL_CHANGES,
    template_name="changeset.html",
    template_dir="wiki",
    extra_context=None,
    is_member=None,
    is_private=None,
    *args,
    **kw,
):
    if request.method == "GET":
        article_args = {"article__title": title}
        if group_slug is not None:
            group = get_object_or_404(group_qs, **{group_slug_field: group_slug})
            article_args.update(
                {"article__content_type": get_ct(group), "article__object_id": group.id}
            )
        changeset = get_object_or_404(
            changes_qs, revision=int(revision), **article_args
        )

        article_args = {"title": title}
        if group_slug is not None:
            group = get_object_or_404(group_qs, **{group_slug_field: group_slug})
            article_args.update({"content_type": get_ct(group), "object_id": group.id})
            allow_read = has_read_perm(request.user, group, is_member, is_private)
            allow_write = has_write_perm(request.user, group, is_member)
        else:
            allow_read = allow_write = True

        if not allow_read:
            return HttpResponseForbidden()

        article = article_qs.get(**article_args)

        if article.deleted:
            return render(
                request, "wiki/gone.html", context={"article": article}, status=410
            )

        if revision_from is None:
            revision_from = int(revision) - 1

        from_value = None
        if int(revision) is not int(revision_from) + 1:
            from_value = revision_from

        template_params = {
            "article": article,
            "article_title": article.title,
            "changeset": changeset,
            "differences": changeset.compare_to(revision_from),
            "from": from_value,
            "to": revision,
            "allow_write": allow_write,
        }

        if group_slug is not None:
            template_params["group"] = group
        if extra_context is not None:
            template_params.update(extra_context)

        return render(
            request,
            "/".join([template_dir, template_name]),
            template_params,
        )
    return HttpResponseNotAllowed(["GET"])


def article_history(
    request,
    title,
    group_slug=None,
    group_slug_field=None,
    group_qs=None,
    article_qs=ALL_ARTICLES,
    template_name="history.html",
    template_dir="wiki",
    extra_context=None,
    is_member=None,
    is_private=None,
    *args,
    **kw,
):
    if request.method == "GET":
        article_args = {"title": title}
        if group_slug is not None:
            group = get_object_or_404(group_qs, **{group_slug_field: group_slug})
            article_args.update({"content_type": get_ct(group), "object_id": group.id})
            allow_read = has_read_perm(request.user, group, is_member, is_private)
            allow_write = has_write_perm(request.user, group, is_member)
        else:
            allow_read = allow_write = True

        if not allow_read:
            return HttpResponseForbidden()

        article = get_object_or_404(article_qs, **article_args)

        if article.deleted:
            return render(
                request, "wiki/gone.html", context={"article": article}, status=410
            )

        # changes = article.changeset_set.filter(
        #    reverted=False).order_by('-revision')
        changes = article.changeset_set(manager="official").order_by("-revision")

        template_params = {
            "article": article,
            "changes": changes,
            "allow_write": allow_write,
        }
        if group_slug is not None:
            template_params["group"] = group
        if extra_context is not None:
            template_params.update(extra_context)

        return render(
            request,
            "/".join([template_dir, template_name]),
            template_params,
        )

    return HttpResponseNotAllowed(["GET"])


@login_required
def revert_to_revision(
    request,
    title,
    group_slug=None,
    group_slug_field=None,
    group_qs=None,
    article_qs=ALL_ARTICLES,
    extra_context=None,
    is_member=None,
    is_private=None,
    *args,
    **kw,
):
    if request.method == "POST":
        revision = int(request.POST["revision"])

        article_args = {"title": title}

        group = None
        if group_slug is not None:
            group = get_object_or_404(group_qs, **{group_slug_field: group_slug})
            article_args.update({"content_type": get_ct(group), "object_id": group.id})
            allow_read = has_read_perm(request.user, group, is_member, is_private)
            allow_write = has_write_perm(request.user, group, is_member)
        else:
            allow_read = allow_write = True

        if not (allow_read or allow_write):
            return HttpResponseForbidden()

        article = get_object_or_404(article_qs, **article_args)

        # Check whether there is another Article with the same name to which this article
        # wants to be reverted to. If so: prevent it and show a message.
        old_title = article.changeset_set.filter(revision=revision + 1).get().old_title
        try:
            art = Article.objects.exclude(pk=article.pk).get(title=old_title)
        except Article.DoesNotExist:
            # No existing article found -> reverting possible
            if request.user.is_authenticated:
                article.revert_to(revision, request.user)
            else:
                article.revert_to(revision)
            return redirect(article)
        # An article with this name exists
        messages.error(
            request,
            "Reverting not possible because an article with name '%s' already exists"
            % old_title,
        )
        return redirect(article)

    return HttpResponseNotAllowed(["POST"])


def history(
    request,
    group_slug=None,
    group_slug_field=None,
    group_qs=None,
    article_qs=ALL_ARTICLES,
    changes_qs=OFFICIAL_CHANGES,
    template_name="recentchanges.html",
    template_dir="wiki",
    extra_context=None,
    *args,
    **kw,
):
    if request.method == "GET":
        if group_slug is not None:
            group = get_object_or_404(group_qs, **{group_slug_field: group_slug})
            changes_qs = changes_qs.filter(
                article__content_type=get_ct(group), article__object_id=group.id
            )
            allow_read = has_read_perm(request.user, group, is_member, is_private)
            allow_write = has_write_perm(request.user, group, is_member)
        else:
            allow_read = allow_write = True

        if not allow_read:
            return HttpResponseForbidden()

        template_params = {
            "changes": changes_qs.order_by("-modified"),
            "allow_write": allow_write,
        }
        if group_slug is not None:
            template_params["group"] = group_slug

        if extra_context is not None:
            template_params.update(extra_context)

        template_params.update(get_pagination(request, template_params["changes"]))

        return render(
            request,
            "/".join([template_dir, template_name]),
            template_params,
        )
    return HttpResponseNotAllowed(["GET"])


@login_required
def observe_article(
    request,
    title,
    group_slug=None,
    group_slug_field=None,
    group_qs=None,
    article_qs=ALL_ARTICLES,
    template_name="recentchanges.html",
    template_dir="wiki",
    extra_context=None,
    is_member=None,
    is_private=None,
    *args,
    **kw,
):
    article_args = {"title": title}
    group = None
    if group_slug is not None:
        group = get_object_or_404(group_qs, **{group_slug_field: group_slug})
        article_args.update({"content_type": get_ct(group), "object_id": group.id})
        allow_read = has_read_perm(request.user, group, is_member, is_private)
    else:
        allow_read = True

    if not allow_read:
        return HttpResponseForbidden()

    article = get_object_or_404(article_qs, **article_args)

    if not notification.is_observing(article, request.user):
        notification.observe(article, request.user, "wiki_observed_article_changed")

    return redirect(article)

    return HttpResponseNotAllowed(["POST"])


@login_required
def stop_observing_article(
    request,
    title,
    group_slug=None,
    group_slug_field=None,
    group_qs=None,
    article_qs=ALL_ARTICLES,
    template_name="recentchanges.html",
    template_dir="wiki",
    extra_context=None,
    is_member=None,
    is_private=None,
    *args,
    **kw,
):
    article_args = {"title": title}
    group = None
    if group_slug is not None:
        group = get_object_or_404(group_qs, **{group_slug_field: group_slug})
        article_args.update({"content_type": get_ct(group), "object_id": group.id})
        allow_read = has_read_perm(request.user, group, is_member, is_private)
    else:
        allow_read = True

    if not allow_read:
        return HttpResponseForbidden()

    article = get_object_or_404(article_qs, **article_args)

    if notification.is_observing(article, request.user):
        notification.stop_observing(article, request.user)

    return redirect(article)


def article_preview(request):
    """This is a AJAX function that previews the body of the article as it is
    currently displayed.

    This function is actually pretty simple, it just runs the function
    through the view template and returns it to the caller

    """
    rv = do_wl_markdown(request.POST["body"], "bleachit")
    return HttpResponse(rv, content_type="text/html")


def article_diff(request):
    """This is a AJAX function that diffs the body of the article as it is
    currently displayed with the current version of the article."""
    current_article = get_object_or_404(Article, pk=int(request.POST["article"]))
    content = request.POST["body"]

    diffs = dmp.diff_main(current_article.content, content)
    dmp.diff_cleanupSemantic(diffs)

    return HttpResponse(dmp.diff_prettyHtml(diffs), content_type="text/html")


def backlinks(request, title):
    """Search for links in other wiki articles pointing to the
    current article.
    """

    # Find old title(s) of this article
    this_article = get_object_or_404(Article, title=title)

    if this_article.deleted:
        return render(
            request, "wiki/gone.html", context={"article": this_article}, status=410
        )

    changesets = this_article.changeset_set.all()
    old_titles = []
    for cs in changesets:
        if cs.old_title and cs.old_title != title and cs.old_title not in old_titles:
            old_titles.append(cs.old_title)

    # Search for semantic wiki links. The regexpr was copied from there
    # and slightly modified
    search_title = [re.compile(r"\[\[\s*(%s)/?\s*(\|\s*.+?\s*)?\]\]" % title)]

    # Search for links in MarkDown syntax, like [Foo](wiki/FooBar)
    # The regexpr matches the title between '/' and ')'
    search_title.append(re.compile(r"\/%s\)" % title))

    # Search for current and previous titles
    found_old_links = []
    found_links = []
    articles_all = Article.objects.all().exclude(title=title, deleted=True)
    for article in articles_all:
        for regexp in search_title:
            # Need to unquote the content to match
            # e.g. [[ Back | Title%20of%20Page ]]
            match = regexp.search(urllib.parse.unquote(article.content))
            if match:
                found_links.append({"title": article.title})

        for old_title in old_titles:
            if old_title in article.content:
                found_old_links.append({"old_title": old_title, "title": article.title})

    context = {
        "found_links": found_links,
        "found_old_links": found_old_links,
        "name": title,
        "article": this_article,
    }
    return render(
        request,
        "wiki/backlinks.html",
        context,
    )


@login_required
def trash_list(request):
    """Renders a list of articles which are deleted.
    Some articles might be redirected to a URL or path outside our wiki. For
    those articles the destination is shown.
    """

    if not request.user.is_staff:
        return HttpResponseForbidden()

    del_articles = Article.objects.filter(deleted=True)
    redirects = Redirect.objects.all()
    articles = []
    for a in del_articles:
        article = [a, None]
        for r in redirects:
            if a.get_absolute_url() == r.old_path:
                article[1] = r
        articles.append(article)

    context = {"articles": articles}

    return render(
        request,
        "wiki/trash_list.html",
        context,
    )
