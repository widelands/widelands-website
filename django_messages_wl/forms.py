from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django_messages.forms import ComposeForm
from django_messages.models import Message

from check_input.models import SuspiciousInput
from mainpage.validators import check_utf8mb3


class ExtendedComposeForm(ComposeForm):
    def __init__(self, *args, sender, **kwargs):
        super().__init__(*args, **kwargs)
        self.sender = sender
        self.fields["body"].validators.append(check_utf8mb3)
        self.fields["subject"].validators.append(check_utf8mb3)

    def clean(self):
        cleaned_data = super().clean()
        # Only check otherwise sendable messages, so that fixing e.g. a typo
        # in the recipient does not flag the same text twice.
        if self.errors:
            return cleaned_data
        # Suspicious messages are refused rather than held: a message has no
        # hidden state, so the record has no object.
        if SuspiciousInput.check_input(
            content_type=ContentType.objects.get_for_model(Message),
            user=self.sender,
            text=f"{cleaned_data['subject']}\n{cleaned_data['body']}",
        ):
            error = "This message looks like spam and was not sent."
            if not self.sender.is_active:
                error += " Your account has been deactivated."
            elif (
                SuspiciousInput.objects.filter(user=self.sender).count()
                == settings.MAX_HIDDEN_POSTS - 1
            ):
                error += " Attention! The next time your account will be deactivated."
            self.add_error("body", error)
        return cleaned_data
