# -*- coding: utf-8 -*-
import re

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from wiki.models import Article
from wiki.models import ChangeSet
from django.conf import settings

try:
    from notification import models as notification
except:
    notification = None


wikiword_pattern = re.compile("^" + settings.WIKI_WORD_RE + "$")


class ArticleForm(forms.ModelForm):

    summary = forms.CharField(widget=forms.Textarea)

    comment = forms.CharField(required=False)

    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.all(), required=False, widget=forms.HiddenInput
    )
    object_id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    action = forms.CharField(widget=forms.HiddenInput)

    redirect_to = forms.CharField(required=False)

    class Meta:
        model = Article
        exclude = ("creator", "group", "created_at", "last_update")

    def clean_title(self):
        """Check for some errors regarding the title:

        1. Check for bad characters
        2. Check for already used titles

        Immediately trying to change the title of a new article to an existing title
        is handled on the database level.

        """

        title = self.cleaned_data["title"]
        if not wikiword_pattern.match(title):
            raise forms.ValidationError(
                _(
                    "Only alphanumeric characters, blank spaces and the underscore are allowed in a title."
                )
            )

        # 'self.initial' contains the prefilled values of the form
        pre_title = self.initial.get("title", None)
        if pre_title != title or not pre_title:
            # Check if the new name has been used already
            cs = ChangeSet.objects.filter(old_title=title)
            if cs:
                raise forms.ValidationError(
                    _(
                        "The title %(title)s is already in use, maybe an other article used to have this name."
                    ),
                    params={"title": title},
                )

        # title not changed, no errors
        return title

    def clean_redirect_to(self):
        redirect_to = self.cleaned_data["redirect_to"]
        if "/wiki/" in redirect_to:
            raise forms.ValidationError(
                _("Only for redirecting outside our wiki."),
            )
        if (
            redirect_to != ""
            and not redirect_to.startswith("/")
            and not redirect_to.startswith("http")
        ):
            raise forms.ValidationError(
                _("The redirect should start with a '/' or 'http'"),
            )
        return redirect_to

    def clean(self):
        super(ArticleForm, self).clean()
        kw = {}
        # After clean_redirect_to() raises a ValidationError the field will be
        # removed from self.cleaned_data
        redirect_to = self.cleaned_data.get("redirect_to", None)
        if redirect_to and not self.cleaned_data["deleted"]:
            self.add_error(
                "deleted", "Applying a redirect needs deleted to be checked."
            )

        if self.cleaned_data["action"] == "create":
            try:
                kw["title"] = self.cleaned_data["title"]
                kw["content_type"] = self.cleaned_data["content_type"]
                kw["object_id"] = self.cleaned_data["object_id"]
            except KeyError:
                pass  # some error in this fields

        return self.cleaned_data

    def cache_old_content(self):
        if self.instance.id is None:
            self.old_title = self.old_content = self.old_markup = ""
            self.is_new = True
        else:
            self.old_title = self.instance.title
            self.old_content = self.instance.content
            self.old_markup = self.instance.markup
            self.is_new = False

    def save(self, *args, **kwargs):
        # 0 - Extra data
        comment = self.cleaned_data["comment"]

        # 2 - Save the Article
        article = super(ArticleForm, self).save(*args, **kwargs)

        # 3 - Set creator and group
        editor = getattr(self, "editor", None)
        group = getattr(self, "group", None)
        if self.is_new:
            if editor is not None:
                article.creator = editor
                article.group = group
            article.save(*args, **kwargs)
            if notification:
                notification.observe(article, editor, "wiki_observed_article_changed")

        # 4 - Create new revision
        changeset = article.new_revision(
            self.old_content, self.old_title, self.old_markup, comment, editor
        )

        return article, changeset
