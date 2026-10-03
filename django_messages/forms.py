from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_messages.fields import CommaSeparatedUserField
from django_messages.models import Message


class ComposeForm(forms.Form):
    """
    A simple default form for private messages.
    """

    recipient = CommaSeparatedUserField(label=_("Recipient"))
    subject = forms.CharField(label=_("Subject"), max_length=140)
    body = forms.CharField(
        label=_("Body"), widget=forms.Textarea(attrs={"rows": "12", "cols": "55"})
    )

    def __init__(self, *args, **kwargs):
        recipient_filter = kwargs.pop("recipient_filter", None)
        super().__init__(*args, **kwargs)
        if recipient_filter is not None:
            self.fields["recipient"]._recipient_filter = recipient_filter

    def save(self, sender, parent_msg=None):
        recipients = self.cleaned_data["recipient"]
        subject = self.cleaned_data["subject"]
        body = self.cleaned_data["body"]
        message_list = []
        for r in recipients:
            msg = Message(
                sender=sender,
                recipient=r,
                subject=subject,
                body=body,
            )
            if parent_msg is not None:
                msg.parent_msg = parent_msg
                parent_msg.replied_at = timezone.now()
                parent_msg.save()
            msg.save()
            message_list.append(msg)
        return message_list
