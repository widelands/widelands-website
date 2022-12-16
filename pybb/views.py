from check_input.models import SuspiciousInput
from collections import OrderedDict
from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from mainpage.templatetags.wl_markdown import do_wl_markdown
from pybb import settings as pybb_settings
from pybb.forms import AddPostForm, EditPostForm, LastPostsDayForm
from pybb.markups import mypostmarkup
from pybb.models import Category, Forum, Topic, Post, Attachment, MARKUP_CHOICES
from pybb.orm import load_related
from pybb.templatetags.pybb_extras import pybb_moderated_by, pybb_editable_by, pybb_has_unreads
from pybb.util import render_to, build_form, quote_text, ajax, urlize, allowed_for
import math


try:
    from notification import models as notification
except ImportError:
    notification = None


def index_ctx(request):
    if allowed_for(request.user):
        cats = Category.objects.all().select_related()
    else:
        cats = Category.exclude_internal.all().select_related()

    return {"cats": cats}


index = render_to("pybb/index.html")(index_ctx)


def show_category_ctx(request, category_id):

    category = get_object_or_404(Category, pk=category_id)

    if category.internal and not allowed_for(request.user):
        raise Http404

    return {"category": category}


show_category = render_to("pybb/category.html")(show_category_ctx)


def show_forum_ctx(request, forum_id):
    forum = get_object_or_404(Forum, pk=forum_id)

    if forum.category.internal and not allowed_for(request.user):
        raise Http404

    user_is_mod = pybb_moderated_by(forum, request.user)

    topics = forum.topics.order_by("-sticky", "-updated").select_related()

    return {
        "forum": forum,
        "topics": topics,
        "page_size": pybb_settings.FORUM_PAGE_SIZE,
        "user_is_mod": user_is_mod,
    }


show_forum = render_to("pybb/forum.html")(show_forum_ctx)


@login_required
def mark_forum_read(request, forum_id):
    user = request.user
    forum = get_object_or_404(Forum, pk=forum_id)
    for topic in forum.topics.all():
        if pybb_has_unreads(topic, user):
            topic.update_read(user)

    return HttpResponseRedirect(forum.get_absolute_url())


def show_topic_ctx(request, topic_id):
    """View of topic posts including a form to add a Post."""

    context = {}
    try:
        topic = Topic.objects.select_related().get(pk=topic_id)
        context.update({"topic": topic})
    except Topic.DoesNotExist:
        raise Http404()

    if topic.forum.category.internal and not allowed_for(request.user):
        raise Http404

    topic.views += 1
    topic.save()

    if request.user.is_authenticated:
        topic.update_read(request.user)

    last_post = topic.posts.order_by("-created")[0]
    context.update({"last_post": last_post})

    initial = {}
    user_is_mod = False
    if request.user.is_authenticated:
        initial = {"markup": "markdown"}

        form = AddPostForm(
            topic=topic,
            initial=initial,
            user=request.user,
        )
        context.update({"form": form})

        user_is_mod = pybb_moderated_by(topic, request.user)
        context.update({"user_is_mod": user_is_mod})

        subscribed = (
            request.user.is_authenticated and request.user in topic.subscribers.all()
        )
        context.update({"subscribed": subscribed})

        is_spam = False
        if topic.is_hidden:
            is_spam = topic.posts.first().is_spam()
        context.update({"is_spam": is_spam})

    if user_is_mod:
        posts = topic.posts.select_related()
    else:
        posts = topic.posts.exclude(hidden=True).select_related()
    context.update({"posts": posts})

    # TODO: fetch profiles
    # profiles = Profile.objects.filter(user__pk__in=
    #     set(x.user.id for x in page.object_list))
    # profiles = dict((x.user_id, x) for x in profiles)

    # for post in page.object_list:
    #     post.user.pybb_profile = profiles[post.user.id]

    if pybb_settings.PYBB_ATTACHMENT_ENABLE:
        load_related(posts, Attachment.objects.all(), "post")

    context.update(
        {
            "page_size": pybb_settings.TOPIC_PAGE_SIZE,
            "form_url": reverse("pybb_add_post", args=[topic.id]),
            "wikipage": settings.ATTACHMENT_DESCR_PAGE,
        }
    )

    return context


show_topic = render_to("pybb/topic.html")(show_topic_ctx)


@login_required
def add_post_ctx(request, forum_id, topic_id):
    """Standalone view for adding posts."""

    forum = None
    topic = None

    if forum_id:
        forum = get_object_or_404(Forum, pk=forum_id)
    elif topic_id:
        topic = get_object_or_404(Topic, pk=topic_id)

    if topic and topic.closed:
        return HttpResponseRedirect(topic.get_absolute_url())

    try:
        quote_id = int(request.GET.get("quote_id"))
    except TypeError:
        quote = ""
    else:
        post = get_object_or_404(Post, pk=quote_id)
        quote = quote_text(post.body, post.user, "markdown")

    form = build_form(
        AddPostForm,
        request,
        topic=topic,
        forum=forum,
        user=request.user,
        initial={"markup": "markdown", "body": quote},
    )

    if form.is_valid():
        post = form.save()

        is_spam = False

        # Check for spam for newly created topics
        if not topic:
            is_spam = SuspiciousInput.check_input(
                content_object=post.topic, user=post.topic.user, text=post.topic.name
            )
        # Check for spam in Post
        if not is_spam:
            is_spam = SuspiciousInput.check_input(
                content_object=post, user=post.user, text=post.body
            )

        if is_spam:
            post.hidden = is_spam
            post.save(update_fields=["hidden"])
            return HttpResponseRedirect("/moderated/")

        if notification:
            if not topic:
                # Inform subscribers of a new topic
                if post.topic.forum.category.internal:
                    # Inform only users which have the permission to enter the
                    # internal forum and superusers. Those users have to:
                    # - enable 'forum_new_topic' in the notification settings, or
                    # - subscribe to an existing topic
                    subscribers = User.objects.filter(
                        Q(groups__permissions__codename=pybb_settings.INTERNAL_PERM)
                        | Q(user_permissions__codename=pybb_settings.INTERNAL_PERM)
                    ).exclude(username=request.user.username)
                    superusers = User.objects.filter(is_superuser=True).exclude(
                        username=request.user.username
                    )
                    # Combine the querysets, excluding double entrys.
                    subscribers = subscribers.union(superusers)
                else:
                    # Inform normal users
                    subscribers = notification.get_observers_for(
                        "forum_new_topic", excl_user=request.user
                    )

                notification.send(
                    subscribers,
                    "forum_new_topic",
                    {"topic": post.topic, "post": post, "user": post.topic.user},
                )
                # Topics author is subscriber for all new posts in his topic
                post.topic.subscribers.add(request.user)

            else:
                # Handle auto subscriptions to topics
                notice_type = notification.NoticeType.objects.get(
                    label="forum_auto_subscribe"
                )
                notice_setting = notification.get_notification_setting(
                    post.user, notice_type, "1"
                )
                if notice_setting.send:
                    post.topic.subscribers.add(request.user)

                # Send mails about a new post to topic subscribers
                notification.send(
                    post.topic.subscribers.exclude(username=post.user),
                    "forum_new_post",
                    {"post": post, "topic": topic, "user": post.user},
                )

        return HttpResponseRedirect(post.get_absolute_url())

    if topic:
        form_url = reverse("pybb_add_post", args=[topic.id])
    else:
        form_url = reverse("pybb_add_topic", args=[forum.id])

    return {
        "form": form,
        "topic": topic,
        "forum": forum,
        "form_url": form_url,
        "wikipage": settings.ATTACHMENT_DESCR_PAGE,
    }


add_post = render_to("pybb/add_post.html")(add_post_ctx)


def show_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count = post.topic.posts.filter(created__lt=post.created).count() + 1
    page = math.ceil(count / float(pybb_settings.TOPIC_PAGE_SIZE))
    url = "%s?page=%d#post-%d" % (
        reverse("pybb_topic", args=[post.topic.id]),
        page,
        post.id,
    )
    return HttpResponseRedirect(url)


@login_required
def edit_post_ctx(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if not pybb_editable_by(post, request.user):
        return HttpResponseRedirect(post.get_absolute_url())

    form = build_form(EditPostForm, request, instance=post)

    if form.is_valid():
        post = form.save()
        is_spam = SuspiciousInput.check_input(
            content_object=post, user=post.user, text=post.body
        )
        if is_spam:
            post.hidden = is_spam
            post.save()
            return HttpResponseRedirect("/moderated/")
        return HttpResponseRedirect(post.get_absolute_url())

    return {
        "form": form,
        "post": post,
    }


edit_post = render_to("pybb/edit_post.html")(edit_post_ctx)


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
    last_post = post.topic.posts.order_by("-created")[0]

    allowed = False
    if pybb_moderated_by(post, request.user) or (
        post.user == request.user and post == last_post
    ):
        allowed = True

    if not allowed:
        return HttpResponseRedirect(post.get_absolute_url())

    if request.method == "POST":
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
        return {
            "post": post,
        }


delete_post = render_to("pybb/delete_post.html")(delete_post_ctx)


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
    if "from_topic" in request.GET:
        return HttpResponseRedirect(reverse("pybb_topic", args=[topic.id]))
    else:
        return HttpResponseRedirect(reverse("pybb_edit_profile"))


@login_required
def add_subscription(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    topic.subscribers.add(request.user)
    return HttpResponseRedirect(reverse("pybb_topic", args=[topic.id]))


def show_attachment(request, hash):
    attachment = get_object_or_404(Attachment, hash=hash)

    with open(attachment.get_absolute_path(), "rb") as file_obj:
        return HttpResponse(file_obj, content_type=attachment.content_type)
    return HTTP404


@login_required
@ajax
def post_ajax_preview(request):
    content = request.POST.get("content")
    markup = request.POST.get("markup")

    if not markup in list(dict(MARKUP_CHOICES).keys()):
        return {"error": "Invalid markup"}

    if not content:
        return {"content": ""}

    if markup == "bbcode":
        html = mypostmarkup.markup(content, auto_urls=False)
    elif markup == "markdown":
        html = str(do_wl_markdown(content, "bleachit"))

    html = urlize(html)
    return {"content": html}


def toggle_hidden_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    first_post = topic.posts.all()[0]
    if first_post.hidden:
        first_post.hidden = False
    else:
        first_post.hidden = True
    first_post.save()

    return redirect(topic)


def all_latest_posts(request):
    """Provide a view to show more latest posts."""

    # default values
    sort_by_default = "topic"
    days_default = pybb_settings.LAST_POSTS_DAYS

    if request.method == "POST":
        # Executed when the form is submitted
        form = LastPostsDayForm(request.POST)
        if form.is_valid():
            days = form.cleaned_data["days"]
            sort_by = form.cleaned_data["sort_by"]
            url = "{}?days={days}&sort_by={sort_by}".format(
                reverse("all_latest_posts"), days=days, sort_by=sort_by
            )

            return HttpResponseRedirect(url)

    else:  # request GET
        # Initialize if no values are given or if the
        # values are given in the url
        days = request.GET.get("days", days_default)
        sort_by = request.GET.get("sort_by", sort_by_default)

        # Create a bound form, so error messages are shown if
        # the given values don't validate against the form
        form = LastPostsDayForm(
            {
                "days": days,
                "sort_by": sort_by,
            }
        )

        if not form.is_valid():
            # If we are here, the user has likely modified the query in the url
            # with invalid values and we apply defaults for the database query
            days = days_default
            sort_by = sort_by_default

    # Executed on every request (POST and GET)
    # We need a try clause here, because one can set invalid values for
    # days in the form.
    try:
        search_date = date.today() - timedelta(int(days))

        # Create a QuerySet with only public posts
        last_posts = Post.objects.public(date_from=search_date)

        posts_count = len(last_posts)

        if sort_by == "topic":
            # The use of an OrderedDict makes sure the ordering of
            # last_posts get not arbitrary
            topics = OrderedDict()
            for post in last_posts:
                if post.topic not in topics:
                    # Create a new key with a list as value
                    topics[post.topic] = [post]
                else:
                    # key exists, just add the post
                    topics[post.topic].append(post)

            object_list = topics

        elif sort_by == "forum":
            forums = OrderedDict()
            for post in last_posts:
                if post.topic.forum.name not in forums:
                    forums[post.topic.forum.name] = OrderedDict({post.topic: [post]})
                elif post.topic not in forums[post.topic.forum.name]:
                    forums[post.topic.forum.name].update({post.topic: [post]})
                else:
                    forums[post.topic.forum.name][post.topic].append(post)

            object_list = forums

    except UnboundLocalError:
        # Needed variables
        object_list = []
        posts_count = 0
        sort_by = sort_by_default

    return {
        "object_list": object_list,
        "posts_count": posts_count,
        "form": form,
        "sort_by": sort_by,
    }


all_latest = render_to("pybb/all_last_posts.html")(all_latest_posts)


@login_required
def all_user_posts(request, this_user=None):
    """Get all posts of a user"""

    if this_user is None:
        posts = Post.objects.public().filter(user__username=request.user)
    else:
        if get_object_or_404(User, username=this_user).wlprofile.deleted:
            raise Http404("User has been deleted")

        posts = Post.objects.public().filter(user__username=this_user)

    return {
        "this_user": this_user,
        "posts": posts,
    }


user_posts = render_to("pybb/all_user_posts.html")(all_user_posts)
