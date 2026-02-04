import datetime
import base64

try:
    import pickle as pickle
except ImportError:
    import pickle

from django.db import models
from django.db.models.query import QuerySet
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail

QUEUE_ALL = getattr(settings, "NOTIFICATION_QUEUE_ALL", False)


class NoticeType(models.Model):
    """A predefined Notice type with fields:

    label: A unique name used to query a NoticeType. E.g. 'forum_new_post'
    display: A short description to display in templates, e.g. 'Forum new Post'
    description: A verbose description, e.g. 'a new comment has been posted to a topic you observe'
    send_default: The default value for NoticeSetting.send. Defaults to True but might be changed
                  by create_notice_type()
    """

    label = models.CharField(_("label"), unique=True, max_length=40)
    display = models.CharField(
        _("display"), max_length=50, help_text=_("Used as subject when sending emails.")
    )
    description = models.CharField(_("description"), max_length=100)
    send_default = models.BooleanField(default=True)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = _("notice type")
        verbose_name_plural = _("notice types")


# Maybe someone wants to be informed by a messenger or whatever the future brings
NOTICE_MEDIA = (("1", _("Email")),)


class NoticeSetting(models.Model):
    """Stores all NoticeSetting's for each NoticeType for all users. Additional fields:

    medium: The medium to send the notice with, defaults to E-Mail
    send: Whether the user wants to receive a notice on the given medium, defaults to
          NoticeType.send_default

    Notice types for each user are added if he/she enters the notification settings page.
    """

    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)
    notice_type = models.ForeignKey(
        NoticeType, verbose_name=_("notice type"), on_delete=models.CASCADE
    )
    medium = models.CharField(
        _("medium"), max_length=1, choices=NOTICE_MEDIA, default="1"
    )
    send = models.BooleanField(_("send"))

    class Meta:
        verbose_name = _("notice setting")
        verbose_name_plural = _("notice settings")
        unique_together = ("user", "notice_type", "medium")


def get_notification_setting(user, notice_type):
    """Return NoticeSetting for a specific user."""
    try:
        return NoticeSetting.objects.get(user=user, notice_type=notice_type)
    except NoticeSetting.DoesNotExist:
        setting = NoticeSetting(
            user=user, notice_type=notice_type, send=notice_type.send_default
        )
        setting.save()
        return setting


def should_send(user, notice_type):
    return get_notification_setting(user, notice_type).send


def get_observers_for(notice_type, excl_user=None):
    """Returns the list of users which wants to get a message (email) for this
    NoticeType."""
    query = NoticeSetting.objects.filter(notice_type__label=notice_type, send=True)

    if excl_user:
        query = query.exclude(user=excl_user)

    return [notice_setting.user for notice_setting in query]


class NoticeQueueBatch(models.Model):
    """A queued notice.

    Denormalized data for a notice.

    """

    pickled_data = models.TextField()


def create_notice_type(label, display, description, send_default=True):
    """Creates a new NoticeType.

    This is intended to be used by other apps as a post_migrate
    manangement step.

    """
    try:
        notice_type = NoticeType.objects.get(label=label)
        updated = False
        if display != notice_type.display:
            notice_type.display = display
            updated = True
        if description != notice_type.description:
            notice_type.description = description
            updated = True
        if send_default != notice_type.send_default:
            notice_type.send_default = send_default
            updated = True
        if updated:
            notice_type.save()
            print(f"Updated NoticeType: {label}")
    except NoticeType.DoesNotExist:
        NoticeType(
            label=label,
            display=display,
            description=description,
            send_default=send_default,
        ).save()
        print(f"Created NoticeType: {label}")


def get_formatted_messages(formats, label, context):
    """Returns a dictionary with the format identifier as the key.

    The values are fully rendered templates with the given context.

    """
    format_templates = {}

    for format in formats:
        # Switch off escaping for .txt templates was done here, but now it
        # resides in the templates
        format_templates[format] = render_to_string(
            (f"notification/{label}/{format}", f"notification/{format}"),
            context,
        )

    return format_templates


def send_now(users, label, extra_context=None, on_site=True):
    """Creates a new notice.

    This is intended to be how other apps create new notices.

    notification.send(user, 'friends_invite_sent', {
        'spam': 'eggs',
        'foo': 'bar',
    )

    You can pass in on_site=False to prevent the notice emitted from being
    displayed on the site.

    """
    if extra_context is None:
        extra_context = {}

    # FrankU: This try statement is added to pass notice types
    # which are deleted but used by third party apps to create a notice
    # e.g. django-messages installed some notice-types which are superfluous
    # because they just create a notice (which is not used anymore), but not
    # used for sending email, like: 'message deleted' or 'message recovered'
    try:
        notice_type = NoticeType.objects.get(label=label)

        current_site = Site.objects.get_current()
        notices_url = f"https://{current_site}{reverse('notification_notices')}"

        formats = (
            "short.txt",  # used for subject
            "full.txt",  # used for email body
            "full_html.txt",
        )  # TODO make formats configurable

        for user in users:
            recipients = []

            # update context with user specific translations
            context = {
                "user": user,
                "current_site": current_site,
                "subject": notice_type.display,
            }
            context.update(extra_context)

            # get prerendered format messages and subjects
            messages = get_formatted_messages(formats, label, context)

            # Create the subject
            # Use 'email_subject.txt' to add Strings in every emails subject
            subject = render_to_string(
                "notification/email_subject.txt",
                {
                    "message": messages["short.txt"],
                },
            ).replace("\n", "")

            # Strip leading newlines. Make writing the email templates easier:
            # Each linebreak in the templates results in a linebreak in the emails
            # If the first line in a template contains only template tags the
            # email will contain an empty line at the top.
            body = render_to_string(
                "notification/email_body.txt",
                {
                    "message": messages["full.txt"],
                    "notices_url": notices_url,
                },
            ).lstrip()

            html_message = render_to_string(
                "notification/email_body_html.txt",
                {
                    "message": messages["full_html.txt"],
                    "notices_url": notices_url,
                },
            )

            if should_send(user, notice_type) and user.email:
                recipients.append(user.email)

            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                recipients,
                fail_silently=True,
                html_message=html_message,
            )

    except NoticeType.DoesNotExist:
        pass


def send(*args, **kwargs):
    """A basic interface around both queue and send_now.

    This honors a global flag NOTIFICATION_QUEUE_ALL that helps
    determine whether all calls should be queued or not. A per call
    ``queue`` or ``now`` keyword argument can be used to always override
    the default global behavior.

    """
    queue_flag = kwargs.pop("queue", False)
    now_flag = kwargs.pop("now", False)
    assert not (queue_flag and now_flag), "'queue' and 'now' cannot both be True."
    if queue_flag:
        return queue(*args, **kwargs)
    elif now_flag:
        return send_now(*args, **kwargs)
    else:
        if QUEUE_ALL:
            return queue(*args, **kwargs)
        else:
            return send_now(*args, **kwargs)


def queue(users, label, extra_context=None, on_site=True):
    """Queue the notification in NoticeQueueBatch.

    This allows for large amounts of user notifications to be deferred
    to a seperate process running outside the webserver.

    """
    if extra_context is None:
        extra_context = {}
    if isinstance(users, QuerySet):
        users = [row["pk"] for row in users.values("pk")]
    else:
        users = [user.pk for user in users]
    notices = []
    for user in users:
        notices.append((user, label, extra_context, on_site))
    data = base64.b64encode(pickle.dumps(notices)).decode("ascii")
    NoticeQueueBatch(pickled_data=data).save()


class ObservedItemManager(models.Manager):
    def all_for(self, observed, signal):
        """Returns all ObservedItems for an observed object, to be sent when a
        signal is emitted."""
        content_type = ContentType.objects.get_for_model(observed)
        observed_items = self.filter(
            content_type=content_type, object_id=observed.id, signal=signal
        )
        return observed_items

    def get_for(self, observed, observer, signal):
        """Returns a single observed item for an observer"""
        content_type = ContentType.objects.get_for_model(observed)
        observed_item = self.get(
            content_type=content_type,
            object_id=observed.id,
            user=observer,
            signal=signal,
        )
        return observed_item


class ObservedItem(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    observed_object = GenericForeignKey("content_type", "object_id")

    notice_type = models.ForeignKey(
        NoticeType, verbose_name=_("notice type"), on_delete=models.CASCADE
    )

    added = models.DateTimeField(_("added"), default=datetime.datetime.now)

    # the signal that will be listened to send the notice
    signal = models.TextField(verbose_name=_("signal"))

    objects = ObservedItemManager()

    class Meta:
        ordering = ["-added"]
        verbose_name = _("observed item")
        verbose_name_plural = _("observed items")

    def send_notice(self):
        send([self.user], self.notice_type.label, {"observed": self.observed_object})

    def get_content_object(self):
        """
        taken from threadedcomments:

        Wrapper around the GenericForeignKey due to compatibility reasons
        and due to ``list_display`` limitations.
        """
        return self.observed_object


def observe(observed, observer, notice_type_label, signal="post_save"):
    """Create a new ObservedItem.

    To be used by applications to register a user as an observer for
    some object.

    """
    notice_type = NoticeType.objects.get(label=notice_type_label)
    observed_item = ObservedItem(
        user=observer, observed_object=observed, notice_type=notice_type, signal=signal
    )
    observed_item.save()
    return observed_item


def stop_observing(observed, observer, signal="post_save"):
    """Remove an observed item."""
    observed_item = ObservedItem.objects.get_for(observed, observer, signal)
    observed_item.delete()


def send_observation_notices_for(observed, signal="post_save"):
    """Send a notice for each registered user about an observed object."""
    observed_items = ObservedItem.objects.all_for(observed, signal)
    for observed_item in observed_items:
        observed_item.send_notice()
    return observed_items


def is_observing(observed, observer, signal="post_save"):
    if isinstance(observer, AnonymousUser):
        return False
    try:
        observed_items = ObservedItem.objects.get_for(observed, observer, signal)
        return True
    except ObservedItem.DoesNotExist:
        return False
    except ObservedItem.MultipleObjectsReturned:
        return True


def handle_observations(sender, instance, *args, **kw):
    send_observation_notices_for(instance)
