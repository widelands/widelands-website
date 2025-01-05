from django.urls import re_path
from threadedcomments import views


urlpatterns = [
    ### Comments ###
    re_path(
        r"^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/$",
        views.comment,
        name="tc_comment",
    ),
    re_path(
        r"^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/$",
        views.comment,
        name="tc_comment_parent",
    ),
    re_path(r"^comment/(?P<edit_id>\d+)/edit/$", views.comment, name="tc_comment_edit"),
    ### Comments (AJAX) ###
    re_path(
        r"^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<ajax>json|xml)/$",
        views.comment,
        name="tc_comment_ajax",
    ),
    re_path(
        r"^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/(?P<ajax>json|xml)/$",
        views.comment,
        name="tc_comment_parent_ajax",
    ),
    re_path(
        r"^comment/(?P<edit_id>\d+)/edit/(?P<ajax>json|xml)/$",
        views.comment,
        name="tc_comment_edit_ajax",
    ),
]
