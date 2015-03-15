from django.shortcuts import render_to_response
from django.template import RequestContext
from settings import WIDELANDS_SVN_DIR
from templatetags.wl_markdown import do_wl_markdown

import sys
import re

def mainpage(request):
    return render_to_response('mainpage.html',
                context_instance=RequestContext(request))


from forms import RegistrationWithCaptchaForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from registration.backends.default import DefaultBackend

def register(request):
    """
    Overwritten view from registration to include a captcha.
    We only need this because the remote IP addr must be passed
    to the form; the registration doesn't do this
    """
    remote_ip = request.META['REMOTE_ADDR']
    if request.method == 'POST':
        form = RegistrationWithCaptchaForm(remote_ip,data=request.POST,
                            files=request.FILES)
        if form.is_valid():
            new_user = DefaultBackend().register(request, **form.cleaned_data)
            return HttpResponseRedirect(reverse('registration_complete'))
    else:
        form = RegistrationWithCaptchaForm(remote_ip)

    return render_to_response("registration/registration_form.html",
                              { 'registration_form': form },
                              context_instance=RequestContext(request))

def developers(request):
    """
    This reads out the authors file in the SVN directory, and returns it
    as a wl_markdown_object. This replaces the wiki developers list
    """
    data = open(WIDELANDS_SVN_DIR, "r").readlines()[4:]
    newdata = []
    for line in data:
        line = line.strip('"_ \n\r').rstrip('" _ \n\r')
        newdata.append(line)

    txt = ''.join(newdata)
    txt,_ = re.subn(r'<\/?rt.*?>', "", txt)
    txt,_ = re.subn(r'<br.*?>', "", txt)
    b = { "24": "\n\n## ",
          "18": "\n\n### ",
          "14": "\n\n#### ",
          "12": "- ",
        }
    e = { "24": "\n\n",
          "18": "\n",
          "14": "\n",
          "12": "\n",
        }
    txt,_ = re.subn(r'<p * font-size=(\d+).*?>(.*?)</p>',
            lambda m: "%s%s%s" %
                    (b[m.group(1)], m.group(2), e[m.group(1)]), txt)
    txt,_ = re.subn(r'<p.*?>(.*?)</p>',
            lambda m: ("- %s\n" % m.group(1) if len(m.group(1).strip()) else "")
                    , txt)

    txt = do_wl_markdown(txt.decode('utf-8'),custom=False)


    return render_to_response("mainpage/developers.html",
                              {"developers": txt},
                              context_instance=RequestContext(request)
    )



def changelog(request):
    """
    This reads out the changelog in the SVN directory, and returns it
    as a wl_markdown_object. This replaces the wiki changelog
    """
    data = open(WIDELANDS_SVN_DIR + "ChangeLog", "r").read()
    return render_to_response("mainpage/changelog.html",
                              {"changelog": data},
                              context_instance=RequestContext(request)
    )

