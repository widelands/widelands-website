from django.conf.urls import url
from threadedcomments import views


urlpatterns = [
    ### Comments ###
    url(
        r"^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/$",
        views.comment,
        name="tc_comment",
    ),
    url(
        r"^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/$",
        views.comment,
        name="tc_comment_parent",
    ),
    url(r"^comment/(?P<edit_id>\d+)/edit/$", views.comment, name="tc_comment_edit"),
    ### Comments (AJAX) ###
    url(
        r"^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<ajax>json|xml)/$",
        views.comment,
        name="tc_comment_ajax",
    ),
    url(
        r"^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/(?P<ajax>json|xml)/$",
        views.comment,
        name="tc_comment_parent_ajax",
    ),
    url(
        r"^comment/(?P<edit_id>\d+)/edit/(?P<ajax>json|xml)/$",
        views.comment,
        name="tc_comment_edit_ajax",
    ),
]
