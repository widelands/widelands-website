from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import SESSION_KEY, logout
from django.contrib.auth.models import User
from check_input.models import SuspiciousInput


def moderate_info(request):
    """Redirect to the moderate comments info page."""

    user = request.user
    if not user.is_authenticated:
        # SuspiciousInput.check_input() deactivates users who reached
        # MAX_HIDDEN_POSTS. The auth middleware no longer resolves them, but
        # their session still holds the user id.
        user = User.objects.filter(
            pk=request.session.get(SESSION_KEY), is_active=False
        ).first()
        if user is None:
            return HttpResponseRedirect("/")

    hidden_posts_count = SuspiciousInput.objects.filter(user=user).count()

    # Don't make the page accesible through browsers addressbar
    if hidden_posts_count == 0:
        return HttpResponseRedirect("/")

    locked = not user.is_active
    if locked:
        logout(request)

    context = {
        "max_count": settings.MAX_HIDDEN_POSTS,
        "act_count": hidden_posts_count,
        "locked": locked,
    }
    return render(request, "check_input/moderate_info.html", context=context)
