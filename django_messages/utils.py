from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.text import wrap
from django.utils.translation import gettext, gettext_lazy as _


def format_quote(sender, body):
    """
    Wraps text at 55 chars and prepends each
    line with `> `.
    Used for quoting messages in replies.
    """
    lines = wrap(body, 55).split("\n")
    for i, line in enumerate(lines):
        lines[i] = "> %s" % line
    quote = "\n".join(lines)
    return gettext("%(sender)s wrote:\n%(body)s") % {"sender": sender, "body": quote}


def new_message_email(
    sender,
    instance,
    signal,
    subject_prefix=_("New Message: %(subject)s"),
    template_name="django_messages/new_message.html",
    default_protocol=None,
    *args,
    **kwargs,
):
    """
    This function sends an email and is called via Django's signal framework.
    Optional arguments:
        ``template_name``: the template to use
        ``subject_prefix``: prefix for the email subject.
        ``default_protocol``: default protocol in site URL passed to template
    """
    if default_protocol is None:
        default_protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")

    if "created" in kwargs and kwargs["created"]:
        try:
            from django.contrib.sites.models import Site

            current_domain = Site.objects.get_current().domain
            subject = subject_prefix % {"subject": instance.subject}
            message = render_to_string(
                template_name,
                {
                    "site_url": "%s://%s" % (default_protocol, current_domain),
                    "message": instance,
                },
            )
            if instance.recipient.email != "":
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [
                        instance.recipient.email,
                    ],
                )
        except Exception:
            pass  # fail silently
