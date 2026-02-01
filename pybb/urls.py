from django.urls import re_path

from pybb import views
from pybb.feeds import LastPosts, LastTopics

urlpatterns = [
    # Misc
    re_path("^$", views.index, name="pybb_index"),
    re_path("^mark_as_read/", views.mark_as_read, name="mark_as_read"),
    re_path(
        r"^category/(?P<category_id>\d+)/$", views.show_category, name="pybb_category"
    ),
    re_path(
        r"^category/(?P<category_id>\d+)/mark_as_read/$",
        views.mark_as_read,
        name="mark_as_read",
    ),
    re_path(r"^forum/(?P<forum_id>\d+)/$", views.show_forum, name="pybb_forum"),
    re_path(
        r"^forum/(?P<forum_id>\d+)/mark_as_read/$",
        views.mark_as_read,
        name="mark_as_read",
    ),
    # Feeds
    re_path(
        r"^feeds/topics/(?P<topic_id>\d+)/$", LastTopics(), name="pybb_feed_topics"
    ),
    re_path(r"^feeds/posts/(?P<topic_id>\d+)/$", LastPosts(), name="pybb_feed_posts"),
    re_path(r"^feeds/topics/$", LastTopics(), name="pybb_feed_topics"),
    re_path(r"^feeds/posts/$", LastPosts(), name="pybb_feed_posts"),
    # Topic
    re_path(r"^topic/(?P<topic_id>\d+)/$", views.show_topic, name="pybb_topic"),
    re_path(
        r"^forum/(?P<forum_id>\d+)/topic/add/$",
        views.add_post,
        {"topic_id": None},
        name="pybb_add_topic",
    ),
    re_path(
        r"^topic/(?P<topic_id>\d+)/stick/$", views.stick_topic, name="pybb_stick_topic"
    ),
    re_path(
        r"^topic/(?P<topic_id>\d+)/unstick/$",
        views.unstick_topic,
        name="pybb_unstick_topic",
    ),
    re_path(
        r"^topic/(?P<topic_id>\d+)/close/$", views.close_topic, name="pybb_close_topic"
    ),
    re_path(
        r"^topic/(?P<topic_id>\d+)/open/$", views.open_topic, name="pybb_open_topic"
    ),
    re_path(
        r"^topic/(?P<topic_id>\d+)/unhide/$",
        views.toggle_hidden_topic,
        name="pybb_toggle_hid_topic",
    ),
    # Post
    re_path(
        r"^topic/(?P<topic_id>\d+)/post/add/$",
        views.add_post,
        {"forum_id": None},
        name="pybb_add_post",
    ),
    re_path(r"^post/(?P<post_id>\d+)/$", views.show_post, name="pybb_post"),
    re_path(r"^post/(?P<post_id>\d+)/edit/$", views.edit_post, name="pybb_edit_post"),
    re_path(
        r"^post/(?P<post_id>\d+)/delete/$", views.delete_post, name="pybb_delete_post"
    ),
    re_path(r"^latest_posts/$", views.all_latest, name="all_latest_posts"),
    re_path(
        r"^user_posts/(?P<this_user>[\w.@+-]+)/$",
        views.user_posts,
        name="all_user_posts",
    ),
    # ajax for Tribute mentions
    re_path("^get_tribute_usernames/", views.get_tribute_usernames),
    # Attachment
    re_path(
        r"^attachment/(?P<hash>\w+)/$", views.show_attachment, name="pybb_attachment"
    ),
    # API
    re_path(
        r"^api/post_ajax_preview/$",
        views.post_ajax_preview,
        name="pybb_post_ajax_preview",
    ),
    # Subscription
    re_path(
        r"^topic/(?P<topic_id>\d+)/subscribe/$",
        views.add_subscription,
        name="pybb_add_subscription",
    ),
    re_path(
        r"^topic/(?P<topic_id>\d+)/unsubscribe/$",
        views.delete_subscription,
        name="pybb_delete_subscription",
    ),
]
