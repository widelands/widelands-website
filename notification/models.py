import datetime

try:
    import pickle as pickle
except ImportError:
    import pickle

from django.db import models
from django.db.models.query import QuerySet
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string

from django.core.exceptions import ImproperlyConfigured

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext, get_language, activate

# favour django-mailer but fall back to django.core.mail
if 'mailer' in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

QUEUE_ALL = getattr(settings, 'NOTIFICATION_QUEUE_ALL', False)


class LanguageStoreNotAvailable(Exception):
    pass


class NoticeType(models.Model):

    label = models.CharField(_('label'), max_length=40)
    display = models.CharField(_('display'),
                               max_length=50,
                               help_text=_('Used as subject when sending emails.'))
    description = models.CharField(_('description'), max_length=100)

    # by default only on for media with sensitivity less than or equal to this
    # number
    default = models.IntegerField(_('default'))

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = _('notice type')
        verbose_name_plural = _('notice types')


# if this gets updated, the create() method below needs to be as well...
NOTICE_MEDIA = (
    ('1', _('Email')),
)

# how spam-sensitive is the medium
NOTICE_MEDIA_DEFAULTS = {
    '1': 2  # email
}


class NoticeSetting(models.Model):
    """Indicates, for a given user, whether to send notifications of a given
    type to a given medium.

    Notice types for each user are added if he/she enters the notification page.

    """

    user = models.ForeignKey(User, verbose_name=_('user'))
    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))
    medium = models.CharField(_('medium'), max_length=1, choices=NOTICE_MEDIA)
    send = models.BooleanField(_('send'))

    class Meta:
        verbose_name = _('notice setting')
        verbose_name_plural = _('notice settings')
        unique_together = ('user', 'notice_type', 'medium')


def get_notification_setting(user, notice_type, medium):
    """Return NotceSetting for a specific user. If a NoticeSetting of
    given NoticeType didn't exist for given user, a NoticeSetting is created.

    If a new NoticeSetting is created, the field 'default' of a NoticeType
    decides whether NoticeSetting.send is True or False as default.
    """
    try:
        return NoticeSetting.objects.get(user=user, notice_type=notice_type, medium=medium)
    except NoticeSetting.DoesNotExist:
        default = (NOTICE_MEDIA_DEFAULTS[medium] <= notice_type.default)
        setting = NoticeSetting(
            user=user, notice_type=notice_type, medium=medium, send=default)
        setting.save()
        return setting


def should_send(user, notice_type, medium):
    return get_notification_setting(user, notice_type, medium).send


def get_observers_for(notice_type, excl_user=None):
    """Returns the list of users which wants to get a message (email) for this
    type of notice."""
    query = NoticeSetting.objects.filter(
            notice_type__label=notice_type, send=True)

    if excl_user:
        query = query.exclude(user=excl_user)

    return [notice_setting.user for notice_setting in query]


class NoticeQueueBatch(models.Model):
    """A queued notice.

    Denormalized data for a notice.

    """
    pickled_data = models.TextField()


def create_notice_type(label, display, description, default=2, verbosity=1):
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
        if default != notice_type.default:
            notice_type.default = default
            updated = True
        if updated:
            notice_type.save()
            if verbosity > 1:
                print('Updated %s NoticeType' % label)
    except NoticeType.DoesNotExist:
        NoticeType(label=label, display=display,
                   description=description, default=default).save()
        if verbosity > 1:
            print('Created %s NoticeType' % label)


def get_notification_language(user):
    """
    Returns site-specific notification language for this user. Raises
    LanguageStoreNotAvailable if this site does not use translated
    notifications.
    """
    if getattr(settings, 'NOTIFICATION_LANGUAGE_MODULE', False):
        try:
            app_label, model_name = settings.NOTIFICATION_LANGUAGE_MODULE.split(
                '.')
            model = models.get_model(app_label, model_name)
            language_model = model._default_manager.get(
                user__id__exact=user.id)
            if hasattr(language_model, 'language'):
                return language_model.language
        except (ImportError, ImproperlyConfigured, model.DoesNotExist):
            raise LanguageStoreNotAvailable
    raise LanguageStoreNotAvailable


def get_formatted_messages(formats, label, context):
    """Returns a dictionary with the format identifier as the key.

    The values are are fully rendered templates with the given context.

    """
    format_templates = {}

    for format in formats:
        # Switch off escaping for .txt templates was done here, but now it
        # resides in the templates
        format_templates[format] = render_to_string((
            'notification/%s/%s' % (label, format),
            'notification/%s' % format), context)

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
        notices_url = "http://%s%s" % (
            str(current_site),
            reverse('notification_notices'),
        )

        current_language = get_language()

        formats = (
            'short.txt', # used for subject
            'full.txt',  # used for email body
        )  # TODO make formats configurable

        for user in users:
            recipients = []
            # get user language for user from language store defined in
            # NOTIFICATION_LANGUAGE_MODULE setting
            try:
                language = get_notification_language(user)
            except LanguageStoreNotAvailable:
                language = None

            if language is not None:
                # activate the user's language
                activate(language)

            # update context with user specific translations
            context = {
                'user': user,
                'current_site': current_site,
                'subject': notice_type.display
            }
            context.update(extra_context)

            # get prerendered format messages and subjects
            messages = get_formatted_messages(formats, label, context)
            
            # Create the subject
            # Use 'email_subject.txt' to add Strings in every emails subject
            subject = render_to_string('notification/email_subject.txt',
                                       {'message': messages['short.txt'],}).replace('\n', '')
            
            # Strip leading newlines. Make writing the email templates easier:
            # Each linebreak in the templates results in a linebreak in the emails
            # If the first line in a template contains only template tags the 
            # email will contain an empty line at the top.
            body = render_to_string('notification/email_body.txt', {
                'message': messages['full.txt'],
                'notices_url': notices_url,
            }).lstrip()

            if should_send(user, notice_type, '1') and user.email:  # Email
                recipients.append(user.email)

            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients)
        
        # reset environment to original language
        activate(current_language)
    except NoticeType.DoesNotExist:
        pass

def send(*args, **kwargs):
    """A basic interface around both queue and send_now.

    This honors a global flag NOTIFICATION_QUEUE_ALL that helps
    determine whether all calls should be queued or not. A per call
    ``queue`` or ``now`` keyword argument can be used to always override
    the default global behavior.

    """
    queue_flag = kwargs.pop('queue', False)
    now_flag = kwargs.pop('now', False)
    assert not (
        queue_flag and now_flag), "'queue' and 'now' cannot both be True."
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
        users = [row['pk'] for row in users.values('pk')]
    else:
        users = [user.pk for user in users]
    notices = []
    for user in users:
        notices.append((user, label, extra_context, on_site))
    NoticeQueueBatch(pickled_data=pickle.dumps(
        notices).encode('base64')).save()


class ObservedItemManager(models.Manager):

    def all_for(self, observed, signal):
        """Returns all ObservedItems for an observed object, to be sent when a
        signal is emited."""
        content_type = ContentType.objects.get_for_model(observed)
        observed_items = self.filter(
            content_type=content_type, object_id=observed.id, signal=signal)
        return observed_items

    def get_for(self, observed, observer, signal):
        content_type = ContentType.objects.get_for_model(observed)
        observed_item = self.get(
            content_type=content_type, object_id=observed.id, user=observer, signal=signal)
        return observed_item


class ObservedItem(models.Model):

    user = models.ForeignKey(User, verbose_name=_('user'))

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    observed_object = GenericForeignKey('content_type', 'object_id')

    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))

    added = models.DateTimeField(_('added'), default=datetime.datetime.now)

    # the signal that will be listened to send the notice
    signal = models.TextField(verbose_name=_('signal'))

    objects = ObservedItemManager()

    class Meta:
        ordering = ['-added']
        verbose_name = _('observed item')
        verbose_name_plural = _('observed items')

    def send_notice(self):
        send([self.user], self.notice_type.label,
             {'observed': self.observed_object})
        
    def get_content_object(self):
        """
        taken from threadedcomments:

        Wrapper around the GenericForeignKey due to compatibility reasons
        and due to ``list_display`` limitations.
        """
        return self.observed_object


def observe(observed, observer, notice_type_label, signal='post_save'):
    """Create a new ObservedItem.

    To be used by applications to register a user as an observer for
    some object.

    """
    notice_type = NoticeType.objects.get(label=notice_type_label)
    observed_item = ObservedItem(user=observer, observed_object=observed,
                                 notice_type=notice_type, signal=signal)
    observed_item.save()
    return observed_item


def stop_observing(observed, observer, signal='post_save'):
    """Remove an observed item."""
    observed_item = ObservedItem.objects.get_for(observed, observer, signal)
    observed_item.delete()


def send_observation_notices_for(observed, signal='post_save'):
    """Send a notice for each registered user about an observed object."""
    observed_items = ObservedItem.objects.all_for(observed, signal)
    for observed_item in observed_items:
        observed_item.send_notice()
    return observed_items


def is_observing(observed, observer, signal='post_save'):
    if isinstance(observer, AnonymousUser):
        return False
    try:
        observed_items = ObservedItem.objects.get_for(
            observed, observer, signal)
        return True
    except ObservedItem.DoesNotExist:
        return False
    except ObservedItem.MultipleObjectsReturned:
        return True


def handle_observations(sender, instance, *args, **kw):
    send_observation_notices_for(instance)
