# -*- coding: utf-8 -*-

from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import (Http404, HttpResponseRedirect,
                         HttpResponseNotAllowed, HttpResponse, HttpResponseForbidden)
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from wiki.forms import ArticleForm
from wiki.models import Article, ChangeSet, dmp

from wiki.utils import get_ct
from django.contrib.auth.decorators import login_required

from wl_utils import get_real_ip
import re

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


def get_articles_by_group(article_qs, group_slug=None,
                          group_slug_field=None, group_qs=None):
    group = None
    if group_slug is not None:
        group = get_object_or_404(group_qs,
                                  **{group_slug_field: group_slug})
        article_qs = article_qs.filter(content_type=get_ct(group),
                                       object_id=group.id)
    return article_qs, group


def get_articles_for_object(object, article_qs=None):
    if article_qs is None:
        article_qs = ALL_ARTICLES
    return article_qs.filter(content_type=get_ct(object),
                             object_id=object.id)


def get_url(urlname, group=None, args=None, kw=None):
    if group is None:
        return reverse(urlname, args=args)
    else:
        app = group._meta.app_label
        urlconf = '.'.join([app, 'urls'])
        url = reverse(urlname, urlconf, kwargs=kw)
        return ''.join(['/', app, url])  # @@@ harcoded: /app/.../

# NOCOMM Franku: This Class is currently not used
# If we want this it has to be checked for the changes
# related to django 1.8.
# A javascript alert box is maybe a better solution


class ArticleEditLock(object):
    """A soft lock to edting an article."""

    def __init__(self, title, request, message_template=None):
        self.title = title
        self.user_ip = get_real_ip(request)
        self.created_at = datetime.now()

        if message_template is None:
            message_template = ('Possible edit conflict:'
                                ' another user started editing this article at %s')

        self.message_template = message_template

        cache.set(title, self, WIKI_LOCK_DURATION * 60)

    def create_message(self, request):
        """Send a message to the user if there is another user editing this
        article."""
        if not self.is_mine(request):
            user = request.user
            user.message_set.create(
                message=self.message_template % self.created_at)

    def is_mine(self, request):
        return self.user_ip == get_real_ip(request)


def has_read_perm(user, group, is_member, is_private):
    """ Return True if the user has permission to *read*
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


def article_list(request,
                 group_slug=None, group_slug_field=None, group_qs=None,
                 article_qs=ALL_ARTICLES,
                 ArticleClass=Article,
                 template_name='index.html',
                 template_dir='wiki',
                 extra_context=None,
                 is_member=None,
                 is_private=None,
                 *args, **kw):
    if request.method == 'GET':
        articles, group = get_articles_by_group(
            article_qs, group_slug,
            group_slug_field, group_qs)

        allow_read = has_read_perm(request.user, group, is_member, is_private)
        allow_write = has_write_perm(request.user, group, is_member)

        if not allow_read:
            return HttpResponseForbidden()

        articles = articles.order_by('title')

        template_params = {'articles': articles,
                           'allow_write': allow_write}

        if group_slug is not None:
            template_params['group'] = group
            new_article = ArticleClass(title='NewArticle',
                                       content_type=get_ct(group),
                                       object_id=group.id)
        else:
            new_article = ArticleClass(title='NewArticle')
        template_params['new_article'] = new_article
        if extra_context is not None:
            template_params.update(extra_context)

        return render_to_response('/'.join([template_dir, template_name]),
                                  template_params,
                                  context_instance=RequestContext(request))
    return HttpResponseNotAllowed(['GET'])


def view_article(request, title, revision=None,
                 ArticleClass=Article,  # to create an unsaved instance
                 group_slug=None, group_slug_field=None, group_qs=None,
                 article_qs=ALL_ARTICLES,
                 template_name='view.html',
                 template_dir='wiki',
                 extra_context=None,
                 is_member=None,
                 is_private=None,
                 *args, **kw):

    if request.method == 'GET':
        article_args = {'title': title}
        if group_slug is not None:
            group = get_object_or_404(
                group_qs, **{group_slug_field: group_slug})
            article_args.update({'content_type': get_ct(group),
                                 'object_id': group.id})
            allow_read = has_read_perm(request.user, group, is_member,
                                       is_private)
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
                article = ChangeSet.objects.filter(
                    old_title=title).order_by('-revision')[0].article
                redirected_from = title
                # if article is not None:
                #    return redirect(article, permanent=True)
            except IndexError:
                article = ArticleClass(**article_args)

        if revision is not None:
            changeset = get_object_or_404(
                article.changeset_set, revision=revision)
            article.content = changeset.get_content()

        template_params = {'article': article,
                           'revision': revision,
                           'redirected_from': redirected_from,
                           'allow_write': allow_write}

        if notification is not None:
            template_params.update({'is_observing': is_observing,
                                    'can_observe': True})

        if group_slug is not None:
            template_params['group'] = group
        if extra_context is not None:
            template_params.update(extra_context)

        return render_to_response('/'.join([template_dir, template_name]),
                                  template_params,
                                  context_instance=RequestContext(request))
    return HttpResponseNotAllowed(['GET'])


@login_required
def edit_article(request, title,
                 group_slug=None, group_slug_field=None, group_qs=None,
                 article_qs=ALL_ARTICLES,
                 ArticleClass=Article,  # to get the DoesNotExist exception
                 ArticleFormClass=ArticleForm,
                 template_name='edit.html',
                 template_dir='wiki',
                 extra_context=None,
                 check_membership=False,
                 is_member=None,
                 is_private=None,
                 *args, **kw):

    group = None
    article_args = {'title': title}
    if group_slug is not None:
        group = get_object_or_404(group_qs, **{group_slug_field: group_slug})
        group_ct = get_ct(group)
        article_args.update({'content_type': group_ct,
                             'object_id': group.id})
        allow_read = has_read_perm(request.user, group, is_member,
                                   is_private)
        allow_write = has_write_perm(request.user, group, is_member)
    else:
        allow_read = allow_write = True

    if not allow_write:
        return HttpResponseForbidden()

    try:
        article = article_qs.get(**article_args)
    except ArticleClass.DoesNotExist:
        article = None

    if request.method == 'POST':

        form = ArticleFormClass(request.POST, instance=article)
        
        form.cache_old_content()
        if form.is_valid():

            if request.user.is_authenticated():
                form.editor = request.user

            if ((article is None) and (group_slug is not None)):
                form.group = group

            new_article, changeset = form.save()

            return redirect(new_article)

    elif request.method == 'GET':
        user_ip = get_real_ip(request)

        # NOCOMM FrankU: Never worked IMHO
        # lock = cache.get(title, None)
        # if lock is None:
        #     lock = ArticleEditLock(title, request)
        # lock.create_message(request)

        initial = {'user_ip': user_ip}
        if group_slug is not None:
            initial.update({'content_type': group_ct.id,
                            'object_id': group.id})

        if article is None:
            initial.update({'title': title,
                            'action': 'create'})
            form = ArticleFormClass(initial=initial)
        else:
            initial['action'] = 'edit'
            form = ArticleFormClass(instance=article,
                                    initial=initial)
    if not article:
        template_params = {'form': form, 'new_article': True}
    else:
        template_params = {'form': form, 'new_article': False,
                           'content_type': ContentType.objects.get_for_model(Article).pk, 'object_id': article.pk,
                           'images': article.all_images(),
                           'article': article,
                           }

    if group_slug is not None:
        template_params['group'] = group
    if extra_context is not None:
        template_params.update(extra_context)

    return render_to_response('/'.join([template_dir, template_name]),
                              template_params,
                              context_instance=RequestContext(request))


def view_changeset(request, title, revision,
                   revision_from=None,
                   group_slug=None, group_slug_field=None, group_qs=None,
                   article_qs=ALL_ARTICLES,
                   changes_qs=ALL_CHANGES,
                   template_name='changeset.html',
                   template_dir='wiki',
                   extra_context=None,
                   is_member=None,
                   is_private=None,
                   *args, **kw):

    if request.method == 'GET':
        article_args = {'article__title': title}
        if group_slug is not None:
            group = get_object_or_404(
                group_qs, **{group_slug_field: group_slug})
            article_args.update({'article__content_type': get_ct(group),
                                 'article__object_id': group.id})
        changeset = get_object_or_404(
            changes_qs,
            revision=int(revision),
            **article_args)

        article_args = {'title': title}
        if group_slug is not None:
            group = get_object_or_404(
                group_qs, **{group_slug_field: group_slug})
            article_args.update({'content_type': get_ct(group),
                                 'object_id': group.id})
            allow_read = has_read_perm(request.user, group, is_member,
                                       is_private)
            allow_write = has_write_perm(request.user, group, is_member)
        else:
            allow_read = allow_write = True

        if not allow_read:
            return HttpResponseForbidden()

        article = article_qs.get(**article_args)

        if revision_from is None:
            revision_from = int(revision) - 1

        from_value = None
        if int(revision) is not int(revision_from) + 1:
            from_value = revision_from

        template_params = {'article': article,
                           'article_title': article.title,
                           'changeset': changeset,
                           'differences': changeset.compare_to(revision_from),
                           'from': from_value,
                           'to': revision,
                           'allow_write': allow_write}

        if group_slug is not None:
            template_params['group'] = group
        if extra_context is not None:
            template_params.update(extra_context)

        return render_to_response('/'.join([template_dir, template_name]),
                                  template_params,
                                  context_instance=RequestContext(request))
    return HttpResponseNotAllowed(['GET'])


def article_history(request, title,
                    group_slug=None, group_slug_field=None, group_qs=None,
                    article_qs=ALL_ARTICLES,
                    template_name='history.html',
                    template_dir='wiki',
                    extra_context=None,
                    is_member=None,
                    is_private=None,
                    *args, **kw):

    if request.method == 'GET':

        article_args = {'title': title}
        if group_slug is not None:
            group = get_object_or_404(
                group_qs, **{group_slug_field: group_slug})
            article_args.update({'content_type': get_ct(group),
                                 'object_id': group.id})
            allow_read = has_read_perm(request.user, group, is_member,
                                       is_private)
            allow_write = has_write_perm(request.user, group, is_member)
        else:
            allow_read = allow_write = True

        if not allow_read:
            return HttpResponseForbidden()

        article = get_object_or_404(article_qs, **article_args)
        # changes = article.changeset_set.filter(
        #    reverted=False).order_by('-revision')
        changes = article.changeset_set.all().order_by('-revision')

        template_params = {'article': article,
                           'changes': changes,
                           'allow_write': allow_write}
        if group_slug is not None:
            template_params['group'] = group
        if extra_context is not None:
            template_params.update(extra_context)

        return render_to_response('/'.join([template_dir, template_name]),
                                  template_params,
                                  context_instance=RequestContext(request))

    return HttpResponseNotAllowed(['GET'])


@login_required
def revert_to_revision(request, title,
                       group_slug=None, group_slug_field=None, group_qs=None,
                       article_qs=ALL_ARTICLES,
                       extra_context=None,
                       is_member=None,
                       is_private=None,
                       *args, **kw):

    if request.method == 'POST':

        revision = int(request.POST['revision'])

        article_args = {'title': title}

        group = None
        if group_slug is not None:
            group = get_object_or_404(
                group_qs, **{group_slug_field: group_slug})
            article_args.update({'content_type': get_ct(group),
                                 'object_id': group.id})
            allow_read = has_read_perm(request.user, group, is_member,
                                       is_private)
            allow_write = has_write_perm(request.user, group, is_member)
        else:
            allow_read = allow_write = True

        if not (allow_read or allow_write):
            return HttpResponseForbidden()

        article = get_object_or_404(article_qs, **article_args)

        
        # Check whether there is another Article with the same name to which this article
        # want's to be reverted to. If so: prevent it and show a message.
        old_title = article.changeset_set.filter(
            revision=revision+1).get().old_title
        try:
            art = Article.objects.exclude(pk=article.pk).get(title=old_title)
        except ObjectDoesNotExist:
            # No existing article found -> reverting possible
            if request.user.is_authenticated():
                article.revert_to(revision, get_real_ip(request), request.user)
            else:
                article.revert_to(revision, get_real_ip(request))
            return redirect(article)
        # An article with this name exists
        messages.error(
            request, 'Reverting not possible because an article with name \'%s\' already exists' % old_title)
        return redirect(article)

    return HttpResponseNotAllowed(['POST'])


def history(request,
            group_slug=None, group_slug_field=None, group_qs=None,
            article_qs=ALL_ARTICLES, changes_qs=ALL_CHANGES,
            template_name='recentchanges.html',
            template_dir='wiki',
            extra_context=None,
            *args, **kw):

    if request.method == 'GET':
        if group_slug is not None:
            group = get_object_or_404(group_qs,
                                      **{group_slug_field: group_slug})
            changes_qs = changes_qs.filter(article__content_type=get_ct(group),
                                           article__object_id=group.id)
            allow_read = has_read_perm(request.user, group, is_member,
                                       is_private)
            allow_write = has_write_perm(request.user, group, is_member)
        else:
            allow_read = allow_write = True

        if not allow_read:
            return HttpResponseForbidden()

        template_params = {'changes': changes_qs.order_by('-modified'),
                           'allow_write': allow_write}
        if group_slug is not None:
            template_params['group'] = group_slug

        if extra_context is not None:
            template_params.update(extra_context)

        return render_to_response('/'.join([template_dir, template_name]),
                                  template_params,
                                  context_instance=RequestContext(request))
    return HttpResponseNotAllowed(['GET'])


@login_required
def observe_article(request, title,
                    group_slug=None, group_slug_field=None, group_qs=None,
                    article_qs=ALL_ARTICLES,
                    template_name='recentchanges.html',
                    template_dir='wiki',
                    extra_context=None,
                    is_member=None,
                    is_private=None,
                    *args, **kw):
    article_args = {'title': title}
    group = None
    if group_slug is not None:
        group = get_object_or_404(group_qs, **{group_slug_field: group_slug})
        article_args.update({'content_type': get_ct(group),
                             'object_id': group.id})
        allow_read = has_read_perm(request.user, group, is_member,
                                   is_private)
    else:
        allow_read = True

    if not allow_read:
        return HttpResponseForbidden()

    article = get_object_or_404(article_qs, **article_args)

    if not notification.is_observing(article, request.user):
        notification.observe(article, request.user,
                             'wiki_observed_article_changed')

    return redirect(article)

    return HttpResponseNotAllowed(['POST'])


@login_required
def stop_observing_article(request, title,
                           group_slug=None, group_slug_field=None, group_qs=None,
                           article_qs=ALL_ARTICLES,
                           template_name='recentchanges.html',
                           template_dir='wiki',
                           extra_context=None,
                           is_member=None,
                           is_private=None,
                           *args, **kw):
    article_args = {'title': title}
    group = None
    if group_slug is not None:
        group = get_object_or_404(group_qs, **{group_slug_field: group_slug})
        article_args.update({'content_type': get_ct(group),
                             'object_id': group.id})
        allow_read = has_read_perm(request.user, group, is_member,
                                   is_private)
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
    rv = do_wl_markdown(request.POST['body'], 'bleachit')
    return HttpResponse(rv, content_type='text/html')


def article_diff(request):
    """This is a AJAX function that diffs the body of the article as it is
    currently displayed with the current version of the article."""
    current_article = get_object_or_404(
        Article, pk=int(request.POST['article']))
    content = request.POST['body']

    diffs = dmp.diff_main(current_article.content, content)
    dmp.diff_cleanupSemantic(diffs)

    return HttpResponse(dmp.diff_prettyHtml(diffs), content_type='text/html')


def backlinks(request, title):
    """Simple text search for links in other wiki articles pointing to the
    current article.

    If we convert WikiWords to markdown wikilinks syntax, this view
    should be changed to use '[[title]]' for searching.

    """

    # Find old title(s) of this article
    this_article = Article.objects.get(title=title)
    changesets = this_article.changeset_set.all()
    old_titles = []
    for cs in changesets:
        if cs.old_title and cs.old_title != title and cs.old_title not in old_titles:
            old_titles.append(cs.old_title)

    # Differentiate between WikiWords and other
    m = re.match(r"(!?)(\b[A-Z][a-z]+[A-Z]\w+\b)", title)
    if m:
        # title is a 'WikiWord' -> This catches also 'MingW' but we have no such title
        search_title = re.compile(r"%s" % title)
    else:
        # Others must be written like links: '[Wiki Page](/wiki/Wiki Page)'
        search_title = re.compile(r"\/%s\)" % title)
    
    # Search for current and previous titles
    found_old_links = []
    found_links = []
    articles_all = Article.objects.all().exclude(title=title)
    for article in articles_all:
        match = search_title.search(article.content)
        if match:
            found_links.append({'title': article.title})
        
        for old_title in old_titles:
            if old_title in article.content:
                found_old_links.append({'old_title': old_title, 'title': article.title })

    context = {'found_links': found_links,
               'found_old_links': found_old_links,
               'name': title}
    return render_to_response('wiki/backlinks.html',
                              context,
                              context_instance=RequestContext(request))
