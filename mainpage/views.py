from django.conf import settings
from .templatetags.wl_markdown import do_wl_markdown
from operator import itemgetter
from django.core.mail import send_mail
from mainpage.forms import ContactForm
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from wl_utils import check_git_path
import subprocess
import sys
import json
import os
import os.path
import locale
import codecs
import random


def mainpage(request):
    context = None
    git_path = check_git_path("git")
    if settings.SHOW_GIT_DATA and git_path:
        try:
            branch = subprocess.check_output(
                [git_path, "symbolic-ref", "--short", "HEAD"]
            )
            commit = subprocess.check_output(
                [git_path, "rev-parse", "--short", "HEAD"]
            )
            context = {
                "git_data": "On branch '{}' with commit '{}'".format(
                    branch.decode(), commit.decode()
                )
            }
        except subprocess.CalledProcessError as e:
            context = {"git_data": e}

    return render(
        request,
        "mainpage/mainpage.html",
        context,
    )


def legal_notice(request):
    """The legal notice page to fullfill law."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["forename"] + " " + form.cleaned_data["surname"]
            subject = "An inquiry over the webpage"
            question = form.cleaned_data["question"]
            answer = form.cleaned_data["answer"]
            message = "\n".join(
                [
                    "From: " + name,
                    "EMail: " + form.cleaned_data["email"],
                    "Question: " + question,
                    "Answer: " + answer,
                    "Inquiry:",
                    form.cleaned_data["inquiry"],
                ]
            )
            sender = "legal_note@widelands.org"

            # get email addresses which are in form of ('name','email'),
            recipients = []
            for recipient in settings.INQUIRY_RECIPIENTS:
                recipients.append(recipient[1])

            # if answer is right send mail
            if check_question(question, answer):
                send_mail(subject, message, sender, recipients, fail_silently=False)
            # else:
            #    # nur zum testen, nach dem ausrollen das else entfernen ;)
            #    send_mail('SPAM: ' + subject, message, sender,
            #          recipients, fail_silently=False)

            # Redirect after POST
            return HttpResponseRedirect("/legal_notice_thanks/")

    else:
        form = ContactForm()  # An unbound form

    # random number for random question
    question_rnum = random.randint(0, len(settings.INQUIRY_QUESTION) - 1)

    return render(
        request,
        "mainpage/legal_notice.html",
        {
            "form": form,
            "inquiry_recipients": settings.INQUIRY_RECIPIENTS,
            "question": settings.INQUIRY_QUESTION[question_rnum][0],
            "chieftains": get_chieftains(),
        },
    )


def check_question(question, answer):
    # check if the answer is right
    questions = settings.INQUIRY_QUESTION
    for i in range(len(questions)):
        if questions[i][0] == question:
            if answer.lower() in questions[i][1 : len(questions[i])]:
                return True
    return False


def get_chieftains():
    # get chieftains from development.json
    # chieftains backup hard coded
    chieftains = settings.INQUIRY_CHIEFTAINS
    try:
        with open(settings.WIDELANDS_SVN_DIR + "data/txts/developers.json", "r") as f:
            json_data = json.load(f)["developers"]

        for head in json_data:
            if head["heading"] == "Chieftains":
                for entry in head["entries"]:
                    if "members" in list(entry.keys()):
                        return entry["members"]

    except IOError:
        chieftains.append("ERROR:")
        chieftains.append("\tCouldn't find developer file!")
        return chieftains


def legal_notice_thanks(request):
    return render(request, "mainpage/legal_notice_thanks.html")


def developers(request):
    """This reads out some json files in the SVN directory, and returns it as a
    wl_markdown_object.

    This replaces the wiki developers list

    """

    # Get locale and translator names from each .json file and
    # store them in one list.
    txt = "[TOC]\n\n"
    transl_files = []
    transl_list = []
    path = os.path.normpath(settings.WIDELANDS_SVN_DIR + "data/i18n/locales/")
    try:
        transl_files = os.listdir(path)
        if transl_files:
            for fname in transl_files:
                if fname.endswith(".json"):
                    with open(path + "/" + fname, "r") as f:
                        json_data = json.load(f)
                    try:
                        if json_data["translator-list"] != "translator-credits":
                            if not "your-language-name-in-english" in json_data:
                                transl_list = ["KeyError"]
                                break
                            transl_list.append(json_data)
                    except KeyError:
                        transl_list = ["KeyError"]
                        break

            # No KeyError -> Sort the list
            if "KeyError" in transl_list:
                txt = "Some Translator key is wrong, please contact the Developers.\n"
            else:
                transl_list.sort(key=itemgetter("your-language-name-in-english"))

        else:
            txt = "No files for translators found!\n"
    except OSError:
        txt = txt + "Couldn't find translators directory!\n"

    # Get other developers, put in the translators list
    # at given position and prepare all for wl_markdown
    try:
        with open(settings.WIDELANDS_SVN_DIR + "data/txts/developers.json", "r") as f:
            json_data = json.load(f)["developers"]

        for head in json_data:
            if "heading" in head:
                # Add first header
                txt = txt + "##" + head["heading"] + "\n"
                # Inserting Translators if there was no error
                if head["heading"] == "Translators" and "KeyError" not in transl_list:
                    for values in transl_list:
                        # Add subheader for locale
                        txt = (
                            txt
                            + "### "
                            + values["your-language-name-in-english"]
                            + "\n"
                        )
                        # Prepaire the names for wl_markdown
                        txt = (
                            txt
                            + "* "
                            + values["translator-list"].replace("\n", "\n* ")
                            + "\n"
                        )

                # Add a subheader or/and the member(s)
                for entry in head["entries"]:
                    if "subheading" in list(entry.keys()):
                        txt = txt + "###" + entry["subheading"] + "\n"
                    if "members" in list(entry.keys()):
                        for name in entry["members"]:
                            txt = txt + "* " + name + "\n"
                    if "translate" in list(entry.keys()):
                        for transl in entry["translate"]:
                            txt = txt + "* " + transl + "\n"

    except IOError:
        txt = txt + "Couldn't find developer file!"

    txt = do_wl_markdown(txt, beautify=False)

    return render(request, "mainpage/developers.html", {"developers": txt})


def changelog(request):
    """This reads out the changelog in the SVN directory, and returns it as a
    wl_markdown_object.

    This replaces the wiki changelog

    """
    data = codecs.open(
        settings.WIDELANDS_SVN_DIR + "ChangeLog", encoding="utf-8", mode="r"
    ).read()
    return render(
        request,
        "mainpage/changelog.html",
        {"changelog": data},
    )


def custom_http_500(request):
    """A custom http 500 error page to not lose css styling."""
    return render(request, "500.html", status=500)


def view_locale(request):
    loc_info = (
        "getlocale: "
        + str(locale.getlocale())
        + "<br/>getdefaultlocale(): "
        + str(locale.getdefaultlocale())
        + "<br/>fs_encoding: "
        + str(sys.getfilesystemencoding())
        + "<br/>sys default encoding: "
        + str(sys.getdefaultencoding())
        + "<br><br> Environment variables:"
        + "<br>DISPLAY: "
        + os.environ.get("DISPLAY", "Not set")
    )
    return HttpResponse(loc_info)
