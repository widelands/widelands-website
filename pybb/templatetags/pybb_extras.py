# coding=UTF-8

from datetime import datetime, timedelta
import re
from pprint import pprint

from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.template.defaultfilters import stringfilter
from django.utils.encoding import smart_unicode
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.utils import dateformat

from pybb.models import Post, Forum, Topic, Read, PrivateMessage
from pybb.unread import cache_unreads
from pybb import settings as pybb_settings

register = template.Library()


@register.tag
def pybb_time(parser, token):
    try:
        tag, time = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'pybb_time requires single argument')
    else:
        return PybbTimeNode(time)


class PybbTimeNode(template.Node):

    def __init__(self, time):
        self.time = template.Variable(time)

    def render(self, context):
        time = self.time.resolve(context)

        delta = datetime.now() - time
        today = datetime.now().replace(hour=0, minute=0, second=0)
        yesterday = today - timedelta(days=1)

        if delta.days == 0:
            if delta.seconds < 60:
                if context['LANGUAGE_CODE'].startswith('ru'):
                    msg = _('seconds ago,seconds ago,seconds ago')
                    import pytils
                    msg = pytils.numeral.choose_plural(delta.seconds, msg)
                else:
                    msg = _('seconds ago')
                return u'%d %s' % (delta.seconds, msg)

            elif delta.seconds < 3600:
                minutes = int(delta.seconds / 60)
                if context['LANGUAGE_CODE'].startswith('ru'):
                    msg = _('minutes ago,minutes ago,minutes ago')
                    import pytils
                    msg = pytils.numeral.choose_plural(minutes, msg)
                else:
                    msg = _('minutes ago')
                return u'%d %s' % (minutes, msg)
        if time > today:
            return _('today, %s') % time.strftime('%H:%M')
        elif time > yesterday:
            return _('yesterday, %s') % time.strftime('%H:%M')
        else:
            return dateformat.format(time, 'd M, Y H:i')


@register.inclusion_tag('pybb/pagination.html', takes_context=True)
def pybb_pagination(context, label):
    page = context['page']
    paginator = context['paginator']
    return {'page': page,
            'paginator': paginator,
            'label': label,
            }
import time


@register.inclusion_tag('pybb/last_posts.html', takes_context=True)
def pybb_last_posts(context, number=5):
    last_posts = Post.objects.filter(hidden=False).order_by(
        '-created').select_related()[:45]
    check = []
    answer = []
    for post in last_posts:
        if (post.topic_id not in check) and len(check) < 5:
            check = check + [post.topic_id]
            answer = answer + [post]
    return {
        'posts': answer,
    }


@register.simple_tag
def pybb_link(object, anchor=u''):
    """Return A tag with link to object."""

    url = hasattr(
        object, 'get_absolute_url') and object.get_absolute_url() or None
    anchor = anchor or smart_unicode(object)
    return mark_safe('<a href="%s">%s</a>' % (url, escape(anchor)))


@register.filter
def pybb_has_unreads(topic, user):
    """Check if topic has messages which user didn't read."""

    now = datetime.now()
    delta = timedelta(seconds=pybb_settings.READ_TIMEOUT)

    def _is_topic_read(topic, user):
        if (now - delta > topic.updated):
            return True
        else:
            if hasattr(topic, '_read'):
                read = topic._read
            else:
                try:
                    read = Read.objects.get(user=user, topic=topic)

                except Read.DoesNotExist:
                    read = None

            if read is None:
                return False
            else:
                return topic.updated <= read.time

    if not user.is_authenticated():
        return False
    else:
        if isinstance(topic, Topic):
            return not _is_topic_read(topic, user)
        if isinstance(topic, Forum):
            forum = topic
            for t in forum.topics.exclude(posts__hidden=True):
                rv = _is_topic_read(t, user)

                if rv == False:
                    return True
            return False
        else:
            raise Exception('Object should be a topic')


@register.filter
def pybb_setting(name):
    return mark_safe(getattr(pybb_settings, name, 'NOT DEFINED'))


@register.filter
def pybb_moderated_by(topic, user):
    """Check if user is moderator of topic's forum."""

    return user.is_superuser or user in topic.forum.moderators.all()


@register.filter
def pybb_editable_by(post, user):
    """Check if the post could be edited by the user."""

    if user.is_superuser:
        return True
    if post.user == user:
        return True
    if user in post.topic.forum.moderators.all():
        return True
    return False


@register.filter
def pybb_posted_by(post, user):
    """Check if the post is writed by the user."""

    return post.user == user


@register.filter
def pybb_equal_to(obj1, obj2):
    """Check if objects are equal."""

    return obj1 == obj2


@register.filter
def pybb_unreads(qs, user):
    return cache_unreads(qs, user)


@register.filter
@stringfilter
def pybb_cut_string(value, arg):
    if len(value) > arg:
        return value[0:arg - 3] + '...'
    else:
        return value


@register.filter
@stringfilter
def pybb_output_bbcode(post):
    """
    post = post.replace('[b]', '<span class="bold">')
    post = post.replace('[i]', '<span class="italic">')
    post = post.relpace('[u]', '<span class="underline">')

    post = post.replace('[/b]', '</span>')
    post = post.replace('[/i]', '</span>')
    post = post.replace('[/u]', '</span>')
    """
    return pprint(post)


@register.simple_tag
def pybb_render_post(post, mode='html'):
    """Process post contents and replace special tags with human readeable
    messages.

    Arguments:
        post - the ``Post`` instance
        mode - "html" or "text". Control which field to use ``body_html`` or ``body_text``

    Currently following tags are supported:

        @@@AUTOJOIN-(SECONDS)@@@ - autojoin message

    """

    def render_autojoin_message(match):
        time_diff = int(match.group(1)) / 60

        join_message = ungettext(u"Added after %s minute",
                                 u"Added after %s minutes",
                                 time_diff)
        join_message %= time_diff

        if mode == 'html':
            return u'<div class="autojoin-message">%s</div>' % join_message
        else:
            return join_message

    body = getattr(post, 'body_%s' % mode)
    re_tag = re.compile(r'@@@AUTOJOIN-(\d+)@@@')
    return re_tag.sub(render_autojoin_message, body)

"""
Spielwiese, Playground, Cour de récréati ;)
"""


@register.filter
@stringfilter
def pybb_trim_string(value, arg):
    """
    Mit "arg" ist es moeglich 1 oder mehr Werte der Funtion zu Uebergeben. Wenn
    mehr als 1 Wert genutzt werden soll wird es durch "-" getrennt. Jeder Wert
    kann entweder die Beschraenkung fuer die Zeichen oder Woerter beinhalten.
    Um das eindeutig zu identifizieren Wort "w" und Zeichen "z".
    Beispiel:
    1. w:10         -> Auf 10 Worte beschraenken
    2. z:250        -> Auf 250 Zeichen beschraenken
    3. w:10-z:250   -> Auf 10 Worte und 250 Zeichen beschraenken

    Beim spaeteren drueber nachdenken ist das mit den Worten eig. egal und
    koennte wieder entfernt werden, aber vllt findet ja einer noch einen nutzen
    dafuer ;)
    """
    _iWord = ''
    _iSign = ''
    _lArguments = arg.split('-')
    _sOption = _lArguments[0].split(':')[0]
    _iValue = _lArguments[0].split(':')[1]
    if len(_lArguments) == 1:
        if _sOption == 'w':
            _iWord = int(_iValue)
        elif _sOption == 'z':
            _iSign = int(_iValue)
        else:
            pass
    elif len(_lArguments) == 2:
        if _sOption == 'w':
            _iWord = int(_iValue)
            _iSign = int(_lArguments[1].split(':')[1])
        elif _sOption == 'z':
            _iSign = int(_iValue)
            _iWord = int(_lArguments[1].split(':')[1])
        else:
            pass
    else:
        pass
    if _iWord != '' or _iSign != '':
        _iWordCount = int(len(value.split(' ')))
        _iSignCount = int(len(value))
        """
        Hier waere noch die Ueberlegung wenn 2 Werte gesetzt das man dann
        wirklich nur ganze Woerter anzeigen laesst ohne sie zu beschneiden
        """
        if _iWord != '' and _iSign != '' and _iSignCount >= _iSign:
            return value[0:_iSign] + '...'
        elif _iWord != '' and _iSign == '' and _iWordCount >= _iWord:
            return ' '.join(value.split(' ')[0:_iWord]) + '...'
        elif _iWord == '' and _iSign != '' and _iSignCount >= _iSign:
            return value[0:_iSign] + '...'
        else:
            return value
            # return " " + str(len(value)) + " " + str(len(value.split(" "))) +
            # " " + str(arg) + " " + str(_iWord) + ":" + str(_iWordCount) + " "
            # + str(_iSign) + ":" + str(_iSignCount)
    else:
        return value
