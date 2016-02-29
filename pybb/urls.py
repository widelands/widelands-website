from django.conf.urls import *

from pybb import views
from pybb.feeds import LastPosts, LastTopics

feeds = {
    'posts': LastPosts,
    'topics': LastTopics,
}

urlpatterns = patterns('',
    # Misc
    url('^$', views.index, name='pybb_index'),
    url('^category/(?P<category_id>\d+)/$', views.show_category, name='pybb_category'),
    url('^forum/(?P<forum_id>\d+)/$', views.show_forum, name='pybb_forum'),
    #url('^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
    #    {'feed_dict': feeds}, name='pybb_feed'),

    # Topic
    url('^topic/(?P<topic_id>\d+)/$', views.show_topic, name='pybb_topic'),
    url('^forum/(?P<forum_id>\d+)/topic/add/$', views.add_post,
        {'topic_id': None}, name='pybb_add_topic'),
    url('^topic/(?P<topic_id>\d+)/stick/$', views.stick_topic, name='pybb_stick_topic'),
    url('^topic/(?P<topic_id>\d+)/unstick/$', views.unstick_topic, name='pybb_unstick_topic'),
    url('^topic/(?P<topic_id>\d+)/close/$', views.close_topic, name='pybb_close_topic'),
    url('^topic/(?P<topic_id>\d+)/open/$', views.open_topic, name='pybb_open_topic'),

    # Post
    url('^topic/(?P<topic_id>\d+)/post/add/$', views.add_post,
        {'forum_id': None}, name='pybb_add_post'),
    url('^post/(?P<post_id>\d+)/$', views.show_post, name='pybb_post'),
    url('^post/(?P<post_id>\d+)/edit/$', views.edit_post, name='pybb_edit_post'),
    url('^post/(?P<post_id>\d+)/delete/$', views.delete_post, name='pybb_delete_post'),

    # Attachment
    url('^attachment/(?P<hash>\w+)/$', views.show_attachment, name='pybb_attachment'),

    # API 
    url('^api/post_ajax_preview/$', views.post_ajax_preview, name='pybb_post_ajax_preview'),

    # Subsciption
    url('^topic/(?P<topic_id>\d+)/subscribe/$', views.add_subscription, name='pybb_add_subscription'),
    url('^topic/(?P<topic_id>\d+)/unsubscribe/$', views.delete_subscription, name='pybb_delete_subscription'),
)
