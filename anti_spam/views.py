from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from anti_spam.models import FoundSpam


def moderate_info(request):
    
    hidden_posts_count = FoundSpam.objects.filter(
        user=request.user).count()
    
    if hidden_posts_count >= settings.MAX_HIDDEN_POSTS:
        user = get_object_or_404(User, username=request.user)
        # Set the user inactive so he can't login
        user.is_active = False
        user.save()
        # Log the user out
        logout(request)
        return HttpResponse(status=403)
    return render(request, 'anti_spam/moderate_info.html')
