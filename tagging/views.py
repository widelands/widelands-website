from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView

from tagging.models import Tag
from tagging.models import TaggedItem


class TaggedObjectList(ListView):
    """
    A ``ListView`` of the instances of the configured ``queryset`` or
    ``model`` which are tagged with the tag named by the ``tag`` URL
    keyword argument.

    In addition to the context variables set up by ``ListView``, a ``tag``
    context variable will contain the ``Tag`` instance for the tag.
    """

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, name=self.kwargs["tag"])
        queryset = super().get_queryset()
        tagged_ids = TaggedItem.objects.filter(
            content_type=ContentType.objects.get_for_model(queryset.model),
            tag=self.tag,
        ).values("object_id")
        return queryset.filter(pk__in=tagged_ids)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context
