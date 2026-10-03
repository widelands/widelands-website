from django_registration.backends.activation import views as activation_views
from django_registration.exceptions import ActivationError


class ActivationView(activation_views.ActivationView):
    """Refuse to reactivate accounts that were deactivated on purpose.

    django-registration activates any inactive user with a valid key. Bans
    and self-deletion also only set is_active=False, so a still valid key
    would undo them. An account that was never activated has never logged
    in, so a set last_login means it was deactivated later.
    """

    DISABLED_MESSAGE = "This account has been deactivated and cannot be activated."

    def get_user(self, username):
        user = super().get_user(username)
        if user.last_login is not None or user.wlprofile.deleted:
            raise ActivationError(self.DISABLED_MESSAGE, code="account_disabled")
        return user
