"""
Based on http://www.djangosnippets.org/snippets/595/
by sopelkin
"""

from django import forms
from django.contrib.auth import get_user_model
from django.forms import widgets
from django.utils.translation import gettext_lazy as _


def _username(user):
    return getattr(user, get_user_model().USERNAME_FIELD)


class CommaSeparatedUserInput(widgets.Input):
    input_type = "text"

    def render(self, name, value, **kwargs):
        if value is None:
            value = ""
        elif isinstance(value, (list, tuple)):
            value = ", ".join([_username(user) for user in value])
        return super().render(name, value, **kwargs)


class CommaSeparatedUserField(forms.Field):
    widget = CommaSeparatedUserInput

    def __init__(self, *args, **kwargs):
        recipient_filter = kwargs.pop("recipient_filter", None)
        self._recipient_filter = recipient_filter
        super().__init__(*args, **kwargs)

    def clean(self, value):
        super().clean(value)
        if not value:
            return ""
        if isinstance(value, (list, tuple)):
            return value

        User = get_user_model()
        names = set(value.split(","))
        names_set = set([name.strip() for name in names if name.strip()])
        users = list(User.objects.filter(**{"%s__in" % User.USERNAME_FIELD: names_set}))
        unknown_names = names_set ^ set([_username(user) for user in users])

        recipient_filter = self._recipient_filter
        invalid_users = []
        if recipient_filter is not None:
            for r in users:
                if recipient_filter(r) is False:
                    users.remove(r)
                    invalid_users.append(_username(r))

        if unknown_names or invalid_users:
            raise forms.ValidationError(
                _("The following usernames are incorrect: %(users)s")
                % {"users": ", ".join(list(unknown_names) + invalid_users)}
            )

        return users

    def prepare_value(self, value):
        if value is None:
            value = ""
        elif isinstance(value, (list, tuple)):
            value = ", ".join([_username(user) for user in value])
        return value
