from django.urls import include, re_path

from pybb.feeds import LastTopics, LastPosts

urlpatterns = [
    re_path("^topics/(?P<topic_id>\d+)/$", LastTopics(), name="pybb_feed_topics"),
    re_path("^posts/(?P<topic_id>\d+)/$", LastPosts(), name="pybb_feed_posts"),
    re_path("^topics/$", LastTopics(), name="pybb_feed_topics"),
    re_path("^posts/$", LastPosts(), name="pybb_feed_posts"),
]
