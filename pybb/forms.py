import re
from datetime import datetime
import os.path

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from pybb.models import Topic, Post, Attachment
from pybb import settings as pybb_settings
from django.conf import settings


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
        super(AddPostForm, self).__init__(*args, **kwargs)

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

        post = Post(topic=topic, user=self.user,
                    markup=self.cleaned_data['markup'],
                    body=self.cleaned_data['body'])
        post.save(*args, **kwargs)

        if pybb_settings.ATTACHMENT_ENABLE:
            self.save_attachment(post, self.cleaned_data['attachment'])

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


class LastPostsDayForm(forms.Form):
    days = forms.IntegerField(
        max_value = 1000,
        min_value = 5,
        )
    
    sort_by = forms.ChoiceField(
        #widget = forms.RadioSelect,
        choices = [('forum','Forum'),('topic', 'Topic'),],
        label = 'Sort by:',
        )
