# -*- coding: utf-8 -*-
import re

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from wiki.models import Article
from wiki.models import ChangeSet
from wiki.templatetags.wiki_extras import WIKI_WORD_RE

wikiword_pattern = re.compile('^' + WIKI_WORD_RE + '$')


class ArticleForm(forms.ModelForm):

    summary = forms.CharField(widget=forms.Textarea)

    comment = forms.CharField(required=False)
    user_ip = forms.CharField(widget=forms.HiddenInput)

    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.all(),
        required=False,
        widget=forms.HiddenInput)
    object_id = forms.IntegerField(required=False,
                                   widget=forms.HiddenInput)

    action = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Article
        exclude = ('creator', 'creator_ip',
                   'group', 'created_at', 'last_update')

    def clean_title(self):
        """Check for some errors regarding the title:
            1. Check for bad characters
            2. Check for reserved titles

            Checking for existing articles is done by Django on Database level
            """
        title = self.cleaned_data['title']
        if not wikiword_pattern.match(title):
            raise forms.ValidationError(_('The title contain bad characters.'))

        cs = ChangeSet.objects.filter(old_title=title).count()
        if cs > 0:
            raise forms.ValidationError(
                _('The title %(title)s is reserved for redirects or old links.'), params={'title': title},)
        # No errors
        return title

    def clean(self):
        super(ArticleForm, self).clean()
        kw = {}

        if self.cleaned_data['action'] == 'create':
            try:
                kw['title'] = self.cleaned_data['title']
                kw['content_type'] = self.cleaned_data['content_type']
                kw['object_id'] = self.cleaned_data['object_id']
            except KeyError:
                pass  # some error in this fields

        return self.cleaned_data

    def cache_old_content(self):
        if self.instance.id is None:
            self.old_title = self.old_content = self.old_markup = ''
            self.is_new = True
        else:
            self.old_title = self.instance.title
            self.old_content = self.instance.content
            self.old_markup = self.instance.markup
            self.is_new = False

    def save(self, *args, **kwargs):
        # 0 - Extra data
        editor_ip = self.cleaned_data['user_ip']
        comment = self.cleaned_data['comment']

        # 2 - Save the Article
        article = super(ArticleForm, self).save(*args, **kwargs)

        # 3 - Set creator and group
        editor = getattr(self, 'editor', None)
        group = getattr(self, 'group', None)
        if self.is_new:
            article.creator_ip = editor_ip
            if editor is not None:
                article.creator = editor
                article.group = group
            article.save(*args, **kwargs)

        # 4 - Create new revision
        changeset = article.new_revision(
            self.old_content, self.old_title, self.old_markup,
            comment, editor_ip, editor)

        return article, changeset
