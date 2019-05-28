from django.conf.urls import *

from pybb import views
from pybb.feeds import LastPosts, LastTopics

urlpatterns = [
    # Misc
    url('^$', views.index, name='pybb_index'),
    url('^category/(?P<category_id>\d+)/$',
        views.show_category, name='pybb_category'),
    url('^forum/(?P<forum_id>\d+)/$', views.show_forum, name='pybb_forum'),

    # Feeds
    url('^feeds/topics/(?P<topic_id>\d+)/$',
        LastTopics(), name='pybb_feed_topics'),
    url('^feeds/posts/(?P<topic_id>\d+)/$',
        LastPosts(), name='pybb_feed_posts'),
    url('^feeds/topics/$', LastTopics(), name='pybb_feed_topics'),
    url('^feeds/posts/$', LastPosts(), name='pybb_feed_posts'),

    # Topic
    url('^topic/(?P<topic_id>\d+)/$', views.show_topic, name='pybb_topic'),
    url('^forum/(?P<forum_id>\d+)/topic/add/$', views.add_post,
        {'topic_id': None}, name='pybb_add_topic'),
    url('^topic/(?P<topic_id>\d+)/stick/$',
        views.stick_topic, name='pybb_stick_topic'),
    url('^topic/(?P<topic_id>\d+)/unstick/$',
        views.unstick_topic, name='pybb_unstick_topic'),
    url('^topic/(?P<topic_id>\d+)/close/$',
        views.close_topic, name='pybb_close_topic'),
    url('^topic/(?P<topic_id>\d+)/open/$',
        views.open_topic, name='pybb_open_topic'),
    url('^topic/(?P<topic_id>\d+)/unhide/$',
        views.toggle_hidden_topic, name='pybb_toggle_hid_topic'),

    # Post
    url('^topic/(?P<topic_id>\d+)/post/add/$', views.add_post,
        {'forum_id': None}, name='pybb_add_post'),
    url('^post/(?P<post_id>\d+)/$', views.show_post, name='pybb_post'),
    url('^post/(?P<post_id>\d+)/edit/$', views.edit_post, name='pybb_edit_post'),
    url('^post/(?P<post_id>\d+)/delete/$',
        views.delete_post, name='pybb_delete_post'),
    url(r'^latest_posts/$', views.all_latest, name='all_latest_posts'),
    url(r'^user_posts/(?P<this_user>[\w.@+-]+)/$', views.user_posts, name='all_user_posts'),

    # Attachment
    url('^attachment/(?P<hash>\w+)/$',
        views.show_attachment, name='pybb_attachment'),

    # API
    url('^api/post_ajax_preview/$', views.post_ajax_preview,
        name='pybb_post_ajax_preview'),

    # Subscription
    url('^topic/(?P<topic_id>\d+)/subscribe/$',
        views.add_subscription, name='pybb_add_subscription'),
    url('^topic/(?P<topic_id>\d+)/unsubscribe/$',
        views.delete_subscription, name='pybb_delete_subscription'),
]
