from django import forms
from threadedcomments.models import DEFAULT_MAX_COMMENT_LENGTH
from threadedcomments.models import ThreadedComment
from django.utils.translation import ugettext_lazy as _
from mainpage.validators import check_utf8mb3

class ThreadedCommentForm(forms.ModelForm):
    """
    Form which can be used to validate data for a new ThreadedComment.
    It consists of just two fields: ``comment``, and ``markup``.

    The ``comment`` field is the only one which is required.
    """

    comment = forms.CharField(
        label=_("comment"),
        max_length=DEFAULT_MAX_COMMENT_LENGTH,
        widget=forms.Textarea,
        validators=[
            check_utf8mb3,
            ]
    )

    class Meta:
        model = ThreadedComment
        fields = ("comment", "markup")
