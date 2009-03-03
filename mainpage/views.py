from django.shortcuts import render_to_response
from django.template import RequestContext

def mainpage(request):
    return render_to_response('mainpage.html', context_instance=RequestContext(request))
    
    
from forms import RegistrationWithCaptchaForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def register(request):
    """
    Overwritten view from registration to include a captcha.
    We only need this because the remote IP addr must be passed
    to the form; the registration doesn't do this
    """
    remote_ip = request.META['REMOTE_ADDR']
    if request.method == 'POST':
        form = RegistrationWithCaptchaForm(remote_ip,data=request.POST, files=request.FILES)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse('registration_complete'))
    else:
        form = RegistrationWithCaptchaForm(remote_ip)
    
    context = RequestContext(request)
    return render_to_response("registration/registration_form.html",
                              { 'registration_form': form },
                              context_instance=context)

