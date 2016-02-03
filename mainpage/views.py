from django.shortcuts import render_to_response
from django.template import RequestContext
from settings import WIDELANDS_SVN_DIR, INQUIRY_RECIPIENTS
from templatetags.wl_markdown import do_wl_markdown
from operator import itemgetter
from django.core.mail import send_mail
from mainpage.forms import ContactForm
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import sys
import json
import os
import os.path


def mainpage(request):
    return render_to_response('mainpage.html',
                              context_instance=RequestContext(request))

def legal_notice(request):
    """The legal notice page to fullfill law."""

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['forename'] +  ' ' + form.cleaned_data['surname']
            subject =  'An inquiry over the webpage'
            message = '\n'.join(['From: ' + name,
                                'EMail: ' + form.cleaned_data['email'],
                                'Inquiry:',
                                form.cleaned_data['inquiry']])
            sender = 'legal_note@widelands.org'

            ## get email addresses which are in a tuple of ('name','email'),
            recipients = []
            for recipient in INQUIRY_RECIPIENTS:
                recipients.append(recipient[1])

            send_mail(subject, message, sender,
                recipients, fail_silently=False)
            return HttpResponseRedirect('/legal_notice_thanks/') # Redirect after POST

    else:
        form = ContactForm() # An unbound form

    return render(request, 'mainpage/legal_notice.html', {
        'form': form,
        })

def legal_notice_thanks(request):
    return render(request, 'mainpage/legal_notice_thanks.html')


from forms import RegistrationWithCaptchaForm
from registration.backends.default import DefaultBackend


def register(request):
    """Overwritten view from registration to include a captcha.

    We only need this because the remote IP addr must be passed to the
    form; the registration doesn't do this

    """
    remote_ip = request.META['REMOTE_ADDR']
    if request.method == 'POST':
        form = RegistrationWithCaptchaForm(remote_ip, data=request.POST,
                                           files=request.FILES)
        if form.is_valid():
            new_user = DefaultBackend().register(request, **form.cleaned_data)
            return HttpResponseRedirect(reverse('registration_complete'))
    else:
        form = RegistrationWithCaptchaForm(remote_ip)

    return render_to_response('registration/registration_form.html',
                              {'registration_form': form},
                              context_instance=RequestContext(request))


def developers(request):
    """This reads out some json files in the SVN directory, and returns it as a
    wl_markdown_object.

    This replaces the wiki developers list

    """

    # Get locale and translator names from each .json file and
    # store them in one list.
    txt = ''
    transl_files = []
    transl_list = []
    path = os.path.normpath(WIDELANDS_SVN_DIR + 'data/i18n/locales/')
    try:
        transl_files = os.listdir(path)
        if transl_files:
            for fname in transl_files:
                if fname.endswith('.json'):
                    with open(path + '/' + fname, 'r') as f:
                        json_data = json.load(f)
                    try:
                        if json_data['translator-list'] != 'translator-credits':
                            if not 'your-language-name-in-english' in json_data:
                                transl_list = ['KeyError']
                                break
                            transl_list.append(json_data)
                    except KeyError:
                        transl_list = ['KeyError']
                        break

            # No KeyError -> Sort the list
            if 'KeyError' in transl_list:
                txt = 'Some Translator key is wrong, please contact the Developers.\n'
            else:
                transl_list.sort(key=itemgetter(
                    'your-language-name-in-english'))

        else:
            txt = 'No files for translators found!\n'
    except OSError:
        txt = txt + "Couldn't find translators directory!\n"

    # Get other developers, put in the translators list
    # at given position and prepare all for wl_markdown
    try:
        with open(WIDELANDS_SVN_DIR + 'data/txts/developers.json', 'r') as f:
            json_data = json.load(f)['developers']

        for head in json_data:
            # Add first header
            txt = txt + '##' + head['heading'] + '\n'
            # Inserting Translators if there was no error
            if head['heading'] == 'Translators' and 'KeyError' not in transl_list:
                for values in (transl_list):
                    # Add subheader for locale
                    txt = txt + '### ' + \
                        values['your-language-name-in-english'] + '\n'
                    # Prepaire the names for wl_markdown
                    txt = txt + '* ' + \
                        values['translator-list'].replace('\n', '\n* ') + '\n'

            # Add a subheader or/and the member(s)
            for entry in head['entries']:
                if 'subheading' in entry.keys():
                    txt = txt + '###' + entry['subheading'] + '\n'
                if 'members' in entry.keys():
                    for name in entry['members']:
                        txt = txt + '* ' + name + '\n'
    except IOError:
        txt = txt + "Couldn't find developer file!"

    txt = do_wl_markdown(txt, custom=False)

    return render_to_response('mainpage/developers.html',
                              {'developers': txt},
                              context_instance=RequestContext(request)
                              )


def changelog(request):
    """This reads out the changelog in the SVN directory, and returns it as a
    wl_markdown_object.

    This replaces the wiki changelog

    """
    data = open(WIDELANDS_SVN_DIR + 'ChangeLog', 'r').read()
    return render_to_response('mainpage/changelog.html',
                              {'changelog': data},
                              context_instance=RequestContext(request)
                              )
