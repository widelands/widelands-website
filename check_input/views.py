from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import User
from check_input.models import SuspiciousInput


def moderate_info(request):
    """Redirect to the moderate comments info page."""
    
    # We need the try to catch logged out users
    try:
        hidden_posts_count = SuspiciousInput.objects.filter(
            user=request.user).count()
    except TypeError:
        return render(request, 'mainpage.html')
            
    
    if hidden_posts_count >= settings.MAX_HIDDEN_POSTS:
        user = get_object_or_404(User, username=request.user)
        # Set the user inactive so he can't login
        user.is_active = False
        user.save()
        # Log the user out
        logout(request)
        return HttpResponse(status=403)
    return render(request, 'check_input/moderate_info.html')
