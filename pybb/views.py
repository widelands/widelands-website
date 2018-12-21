import math
from mainpage.templatetags.wl_markdown import do_wl_markdown
from pybb.markups import mypostmarkup

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import redirect
from django.db.models import Q
from django.http import Http404

from pybb.util import render_to, build_form, quote_text, ajax, urlize
from pybb.models import Category, Forum, Topic, Post, Attachment,\
    MARKUP_CHOICES
from pybb.forms import AddPostForm, EditPostForm
from pybb import settings as pybb_settings
from pybb.orm import load_related
from pybb.templatetags.pybb_extras import pybb_moderated_by

from check_input.models import SuspiciousInput

try:
    from notification import models as notification
except ImportError:
    notification = None


def allowed_for(user):
    """Check if a user has the permission to enter internal Forums."""
    
    return user.is_superuser or user.has_perm(pybb_settings.INTERNAL_PERM)


def index_ctx(request):
    if allowed_for(request.user):
        cats = Category.objects.all().select_related()
    else:
        cats = Category.exclude_internal.all().select_related()

    return {'cats': cats }
index = render_to('pybb/index.html')(index_ctx)


def show_category_ctx(request, category_id):
    
    category = get_object_or_404(Category, pk=category_id)
    
    if category.internal and not allowed_for(request.user):
        raise Http404

    return {'category': category }
show_category = render_to('pybb/category.html')(show_category_ctx)


def show_forum_ctx(request, forum_id):
    forum = get_object_or_404(Forum, pk=forum_id)

    if forum.category.internal and not allowed_for(request.user):
        raise Http404

    user_is_mod = pybb_moderated_by(forum, request.user)

    topics = forum.topics.order_by(
        '-sticky', '-updated').select_related()

    return {'forum': forum,
            'topics': topics,
            'page_size': pybb_settings.FORUM_PAGE_SIZE,
            'user_is_mod': user_is_mod,
            }
show_forum = render_to('pybb/forum.html')(show_forum_ctx)


def show_topic_ctx(request, topic_id):
    try:
        topic = Topic.objects.select_related().get(pk=topic_id)
    except Topic.DoesNotExist:
        raise Http404()

    if topic.forum.category.internal and not allowed_for(request.user):
        raise Http404

    topic.views += 1
    topic.save()

    if request.user.is_authenticated:
        topic.update_read(request.user)

    last_post = topic.posts.order_by('-created')[0]

    initial = {}
    if request.user.is_authenticated:
        initial = {'markup': 'markdown'}
    form = AddPostForm(topic=topic, initial=initial)

    user_is_mod = pybb_moderated_by(topic, request.user)
    subscribed = (request.user.is_authenticated and
                  request.user in topic.subscribers.all())

    is_spam = False
    if topic.is_hidden:
            is_spam = topic.posts.first().is_spam()

    if user_is_mod:
        posts = topic.posts.select_related()
    else:
        posts = topic.posts.exclude(hidden=True).select_related()
 
    # TODO: fetch profiles
    # profiles = Profile.objects.filter(user__pk__in=
    #     set(x.user.id for x in page.object_list))
    # profiles = dict((x.user_id, x) for x in profiles)

    # for post in page.object_list:
    #     post.user.pybb_profile = profiles[post.user.id]

    load_related(posts, Attachment.objects.all(), 'post')

    return {'topic': topic,
            'last_post': last_post,
            'form': form,
            'user_is_mod': user_is_mod,
            'subscribed': subscribed,
            'posts': posts,
            'page_size': pybb_settings.TOPIC_PAGE_SIZE,
            'form_url': reverse('pybb_add_post', args=[topic.id]),
            'is_spam': is_spam,
            }
show_topic = render_to('pybb/topic.html')(show_topic_ctx)


@login_required
def add_post_ctx(request, forum_id, topic_id):
    forum = None
    topic = None

    if forum_id:
        forum = get_object_or_404(Forum, pk=forum_id)
    elif topic_id:
        topic = get_object_or_404(Topic, pk=topic_id)

    if topic and topic.closed:
        return HttpResponseRedirect(topic.get_absolute_url())

    try:
        quote_id = int(request.GET.get('quote_id'))
    except TypeError:
        quote = ''
    else:
        post = get_object_or_404(Post, pk=quote_id)
        quote = quote_text(post.body, post.user, 'markdown')

    form = build_form(AddPostForm, request, topic=topic, forum=forum,
                      user=request.user,
                      initial={'markup': 'markdown', 'body': quote})

    if form.is_valid():
        post = form.save()

        is_spam = False
        # Check for spam in topics name for new topics
        if not topic:
            is_spam = SuspiciousInput.check_input(
                content_object=post.topic, user=post.topic.user, text=post.topic.name)
        # Check for spam in Post
        if not is_spam:
            is_spam = SuspiciousInput.check_input(
                content_object=post, user=post.user, text=post.body)

        if is_spam:
            post.hidden = is_spam
            post.save(update_fields=['hidden'])
            return HttpResponseRedirect('/moderated/')

        if notification:
            if not topic:
                # Inform subscribers of a new topic
                if post.topic.forum.category.internal:
                    # Inform only users which have the permission to enter the
                    # internal forum and superusers. Those users have to:
                    # - enable 'forum_new_topic' in the notification settings, or
                    # - subscribe to an existing topic
                    subscribers = User.objects.filter(
                        Q(groups__permissions__codename=pybb_settings.INTERNAL_PERM) |
                        Q(user_permissions__codename=pybb_settings.INTERNAL_PERM)
                        ).exclude(username=request.user.username)
                    superusers = User.objects.filter(
                        is_superuser=True).exclude(
                        username=request.user.username)
                    # Combine the querysets, excluding double entrys.
                    subscribers = subscribers.union(superusers)
                else:
                    # Inform normal users
                    subscribers = notification.get_observers_for('forum_new_topic',
                                                             excl_user=request.user)

                notification.send(subscribers, 'forum_new_topic',
                                  {'topic': post.topic,
                                   'post': post,
                                   'user': post.topic.user
                                   },
                                  queue = True)
                # Topics author is subscriber for all new posts in his topic
                post.topic.subscribers.add(request.user)

            else:
                # Send mails about a new post to topic subscribers
                notification.send(post.topic.subscribers.exclude(username=post.user), 'forum_new_post',
                                  {'post': post, 'topic': topic, 'user': post.user}, queue = True)

        return HttpResponseRedirect(post.get_absolute_url())

    if topic:
        form_url = reverse('pybb_add_post', args=[topic.id])
    else:
        form_url = reverse('pybb_add_topic', args=[forum.id])

    return {'form': form,
            'topic': topic,
            'forum': forum,
            'form_url': form_url,
            }
add_post = render_to('pybb/add_post.html')(add_post_ctx)


def show_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count = post.topic.posts.filter(created__lt=post.created).count() + 1
    page = math.ceil(count / float(pybb_settings.TOPIC_PAGE_SIZE))
    url = '%s?page=%d#post-%d' % (reverse('pybb_topic',
                                          args=[post.topic.id]), page, post.id)
    return HttpResponseRedirect(url)


@login_required
def edit_post_ctx(request, post_id):
    from pybb.templatetags.pybb_extras import pybb_editable_by

    post = get_object_or_404(Post, pk=post_id)
    if not pybb_editable_by(post, request.user):
        return HttpResponseRedirect(post.get_absolute_url())

    form = build_form(EditPostForm, request, instance=post)

    if form.is_valid():
        post = form.save()
        is_spam = SuspiciousInput.check_input(content_object=post, user=post.user, text=post.body)
        if is_spam:
            post.hidden = is_spam
            post.save()
            return HttpResponseRedirect('/moderated/')
        return HttpResponseRedirect(post.get_absolute_url())

    return {'form': form,
            'post': post,
            }
edit_post = render_to('pybb/edit_post.html')(edit_post_ctx)


@login_required
def stick_topic(request, topic_id):

    topic = get_object_or_404(Topic, pk=topic_id)
    if pybb_moderated_by(topic, request.user):
        if not topic.sticky:
            topic.sticky = True
            topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
def unstick_topic(request, topic_id):

    topic = get_object_or_404(Topic, pk=topic_id)
    if pybb_moderated_by(topic, request.user):
        if topic.sticky:
            topic.sticky = False
            topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
def delete_post_ctx(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    last_post = post.topic.posts.order_by('-created')[0]

    allowed = False
    if pybb_moderated_by(post, request.user) or \
            (post.user == request.user and post == last_post):
        allowed = True

    if not allowed:
        return HttpResponseRedirect(post.get_absolute_url())

    if 'POST' == request.method:
        topic = post.topic
        forum = post.topic.forum
        post.delete()

        try:
            Topic.objects.get(pk=topic.id)
        except Topic.DoesNotExist:
            return HttpResponseRedirect(forum.get_absolute_url())
        else:
            return HttpResponseRedirect(topic.get_absolute_url())
    else:
        return {'post': post,
                }
delete_post = render_to('pybb/delete_post.html')(delete_post_ctx)


@login_required
def close_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    if pybb_moderated_by(topic, request.user):
        if not topic.closed:
            topic.closed = True
            topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
def open_topic(request, topic_id):

    topic = get_object_or_404(Topic, pk=topic_id)
    if pybb_moderated_by(topic, request.user):
        if topic.closed:
            topic.closed = False
            topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
def delete_subscription(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    topic.subscribers.remove(request.user)
    if 'from_topic' in request.GET:
        return HttpResponseRedirect(reverse('pybb_topic', args=[topic.id]))
    else:
        return HttpResponseRedirect(reverse('pybb_edit_profile'))


@login_required
def add_subscription(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    topic.subscribers.add(request.user)
    return HttpResponseRedirect(reverse('pybb_topic', args=[topic.id]))


@login_required
def show_attachment(request, hash):
    attachment = get_object_or_404(Attachment, hash=hash)
    file_obj = file(attachment.get_absolute_path())
    return HttpResponse(file_obj, content_type=attachment.content_type)


@login_required
@ajax
def post_ajax_preview(request):
    content = request.POST.get('content')
    markup = request.POST.get('markup')

    if not markup in dict(MARKUP_CHOICES).keys():
        return {'error': 'Invalid markup'}

    if not content:
        return {'content': ''}

    if markup == 'bbcode':
        html = mypostmarkup.markup(content, auto_urls=False)
    elif markup == 'markdown':
        html = unicode(do_wl_markdown(content, 'bleachit'))

    html = urlize(html)
    return {'content': html}


def toggle_hidden_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    first_post = topic.posts.all()[0]
    if first_post.hidden:
        first_post.hidden = False
    else:
        first_post.hidden = True
    first_post.save()
    
    return redirect(topic)
