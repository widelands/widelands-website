from django.shortcuts import render_to_response
from django.template import RequestContext
from settings import WIDELANDS_SVN_DIR
from templatetags.wl_markdown import do_wl_markdown

import sys
import re
import json
import os
import os.path

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
    This reads out some json files in the SVN directory, and returns it
    as a wl_markdown_object. This replaces the wiki developers list
    """
    
    # Get locale and translator names from each .json file and 
    # store them in one list.
    txt = ""
    transl_files = []
    transl_list = []
    path = os.path.normpath(WIDELANDS_SVN_DIR + "txts/translators/")
    try:
        transl_files = os.listdir(path)
        if transl_files:
            for fname in transl_files:
                if fname.endswith(".json"):
                    with open(path + "/" + fname,"r") as f:
                        json_data = json.load(f)["locale-translators"]
    
                    if json_data["translator-list"] != "translator-credits":
                            transl_list.append(json_data)
        else:
            txt = "No files for translators found!"
    except OSError:
        txt = txt + "Couldn't find translators directory!"

               
    # Get other developers, put in the translators list
    # at given position and prepaire all for wl_markdown
    try:
        f = open(WIDELANDS_SVN_DIR + "txts/developers.json", "r")
        json_data = json.load(f)["developers"]
        f.close()
    
        for head in json_data:
            # Add first header
            txt = txt + "##" + head["heading"] + "\n"
            # Inserting Translators
            if head["heading"] == "Translators":
                for values in (transl_list):
                    # Add subheader for locale
                    txt = txt + "### " + values["your-language-name"] + "\n"
                    # Prepaire the names for wl_markdown
                    txt = txt + "* " + values["translator-list"].replace('\n', '\n* ') + "\n"
                    
            # Add a subheader or/and the member(s)
            for entry in head["entries"]:
                if "subheading" in entry.keys():
                    txt = txt + "###" + entry["subheading"] + "\n"
                if "members" in entry.keys():
                    for name in entry["members"]:
                        txt = txt + "* " + name + "\n"
    except IOError:
        txt = txt + "Couldn't find developer file!"
                    
    txt = do_wl_markdown(txt,custom=False)

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

