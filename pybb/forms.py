import re
from datetime import datetime
import os.path

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from pybb.models import Topic, Post, PrivateMessage, Attachment
from pybb import settings as pybb_settings
from django.conf import settings
from notification.models import send, get_observers_for


class AddPostForm(forms.ModelForm):
    name = forms.CharField(label=_('Subject'))
    attachment = forms.FileField(label=_('Attachment'), required=False)

    class Meta:
        model = Post
        # Listing fields again to get the the right order; See also the TODO
        fields = ['name', 'body', 'markup', 'attachment', ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.topic = kwargs.pop('topic', None)
        self.forum = kwargs.pop('forum', None)
        self.ip = kwargs.pop('ip', None)
        super(AddPostForm, self).__init__(*args, **kwargs)

        # TODO(Franku): This doesn't work anymore with django 1.8 Use 'field_order'
        # with django 1.9
        self.fields.keyOrder = ['name',
                                'body',
                                'markup',
                                'attachment']

        if self.topic:
            self.fields['name'].widget = forms.HiddenInput()
            self.fields['name'].required = False

        if not pybb_settings.ATTACHMENT_ENABLE:
            self.fields['attachment'].widget = forms.HiddenInput()
            self.fields['attachment'].required = False

    def clean_attachment(self):
        if self.cleaned_data['attachment']:
            memfile = self.cleaned_data['attachment']
            if memfile.size > pybb_settings.ATTACHMENT_SIZE_LIMIT:
                raise forms.ValidationError(_('Attachment is too big'))
        return self.cleaned_data['attachment']

    def save(self, *args, **kwargs):
        if self.forum:
            topic_is_new = True
            topic = Topic(forum=self.forum,
                          user=self.user,
                          name=self.cleaned_data['name'])
            topic.save(*args, **kwargs)
        else:
            topic_is_new = False
            topic = self.topic

        # Check for spam and hide the post
        # TODO(Franku): This is currently a simple keyword search. Maybe add akismet check here
        # could be improved...
        # The admins get informed of hidden post(s) over
        # a Django command. See pybb/management/commands
        hidden = False
        text = self.cleaned_data['body']
        if any(x in text.lower() for x in settings.ANTI_SPAM_BODY):
            hidden = True

        if re.search(settings.ANTI_SPAM_PHONE_NR, text):
            hidden = True

        if topic_is_new:
            text = self.cleaned_data['name']
            if any(x in text.lower() for x in settings.ANTI_SPAM_TOPIC):
                hidden = True
            if re.search(settings.ANTI_SPAM_PHONE_NR, text):
                hidden = True

        post = Post(topic=topic, user=self.user, user_ip=self.ip,
                    markup=self.cleaned_data['markup'],
                    body=self.cleaned_data['body'], hidden=hidden)
        post.save(*args, **kwargs)

        if pybb_settings.ATTACHMENT_ENABLE:
            self.save_attachment(post, self.cleaned_data['attachment'])

        if not hidden:
            if topic_is_new:
                send(get_observers_for('forum_new_topic'), 'forum_new_topic',
                     {'topic': topic, 'post': post, 'user': topic.user}, queue = True)
            else:
                send(self.topic.subscribers.all(), 'forum_new_post',
                     {'post': post, 'topic': topic, 'user': post.user}, queue = True)

        return post

    def save_attachment(self, post, memfile):
        if memfile:
            obj = Attachment(size=memfile.size, content_type=memfile.content_type,
                             name=memfile.name, post=post)
            dir = os.path.join(settings.MEDIA_ROOT,
                               pybb_settings.ATTACHMENT_UPLOAD_TO)
            fname = '%d.0' % post.id
            path = os.path.join(dir, fname)
            file(path, 'w').write(memfile.read())
            obj.path = fname
            obj.save()


class EditPostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['body', 'markup']

    def save(self, *args, **kwargs):
        post = super(EditPostForm, self).save(commit=False)
        post.updated = datetime.now()
        post.save(*args, **kwargs)
        return post


class UserSearchForm(forms.Form):
    query = forms.CharField(required=False, label='')

    def filter(self, qs):
        if self.is_valid():
            query = self.cleaned_data['query']
            return qs.filter(username__contains=query)
        else:
            return qs
