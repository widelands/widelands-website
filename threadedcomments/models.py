from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.conf import settings

DEFAULT_MAX_COMMENT_LENGTH = getattr(settings, "DEFAULT_MAX_COMMENT_LENGTH", 1000)
DEFAULT_MAX_COMMENT_DEPTH = getattr(settings, "DEFAULT_MAX_COMMENT_DEPTH", 8)

MARKDOWN = 1
TEXTILE = 2
REST = 3
PLAINTEXT = 5
MARKUP_CHOICES = (
    (MARKDOWN, _("markdown")),
    (TEXTILE, _("textile")),
    (REST, _("restructuredtext")),
    (PLAINTEXT, _("plaintext")),
)

DEFAULT_MARKUP = getattr(settings, "DEFAULT_MARKUP", PLAINTEXT)


def dfs(node, all_nodes, depth):
    """
    Performs a recursive depth-first search starting at ``node``.  This function
    also annotates an attribute, ``depth``, which is an integer that represents
    how deeply nested this node is away from the original object.
    """
    node.depth = depth
    to_return = [
        node,
    ]
    for subnode in all_nodes:
        if subnode.parent and subnode.parent.id == node.id:
            to_return.extend(dfs(subnode, all_nodes, depth + 1))
    return to_return


class ThreadedCommentManager(models.Manager):
    """A ``Manager`` which will be attached to each comment model.

    It helps to facilitate the retrieval of comments in tree form and
    also has utility methods for creating and retrieving objects related
    to a specific content object.

    """

    def get_tree(self, content_object, root=None):
        """
        Runs a depth-first search on all comments related to the given content_object.
        This depth-first search adds a ``depth`` attribute to the comment which
        signifies how how deeply nested the comment is away from the original object.

        If root is specified, it will start the tree from that comment's ID.

        Ideally, one would use this ``depth`` attribute in the display of the comment to
        offset that comment by some specified length.

        The following is a (VERY) simple example of how the depth property might be used in a template:

            {% for comment in comment_tree %}
                <p style="margin-left: {{ comment.depth }}em">{{ comment.comment }}</p>
            {% endfor %}
        """
        content_type = ContentType.objects.get_for_model(content_object)
        children = list(
            self.get_query_set()
            .filter(
                content_type=content_type,
                object_id=getattr(content_object, "pk", getattr(content_object, "id")),
            )
            .select_related()
            .order_by("date_submitted")
        )
        to_return = []
        if root:
            if isinstance(root, int):
                root_id = root
            else:
                root_id = root.id
            to_return = [c for c in children if c.id == root_id]
            if to_return:
                to_return[0].depth = 0
                for child in children:
                    if child.parent_id == root_id:
                        to_return.extend(dfs(child, children, 1))
        else:
            for child in children:
                if not child.parent:
                    to_return.extend(dfs(child, children, 0))
        return to_return

    def _generate_object_kwarg_dict(self, content_object, **kwargs):
        """Generates the most comment keyword arguments for a given
        ``content_object``."""
        kwargs["content_type"] = ContentType.objects.get_for_model(content_object)
        kwargs["object_id"] = getattr(
            content_object, "pk", getattr(content_object, "id")
        )
        return kwargs

    def create_for_object(self, content_object, **kwargs):
        """A simple wrapper around ``create`` for a given
        ``content_object``."""
        return self.create(**self._generate_object_kwarg_dict(content_object, **kwargs))

    def get_or_create_for_object(self, content_object, **kwargs):
        """A simple wrapper around ``get_or_create`` for a given
        ``content_object``."""
        return self.get_or_create(
            **self._generate_object_kwarg_dict(content_object, **kwargs)
        )

    def get_for_object(self, content_object, **kwargs):
        """A simple wrapper around ``get`` for a given ``content_object``."""
        return self.get(**self._generate_object_kwarg_dict(content_object, **kwargs))

    def all_for_object(self, content_object, **kwargs):
        """Prepopulates a QuerySet with all comments related to the given
        ``content_object``."""
        return self.filter(**self._generate_object_kwarg_dict(content_object, **kwargs))


class PublicThreadedCommentManager(ThreadedCommentManager):
    """
    A ``Manager`` which borrows all of the same methods from ``ThreadedCommentManager``,
    but which also restricts the queryset to only the published methods
    (in other words, ``is_public = True``).
    """

    def get_query_set(self):
        return (
            super(ThreadedCommentManager, self)
            .get_queryset()
            .filter(Q(is_public=True) | Q(is_approved=True))
        )


class ThreadedComment(models.Model):
    """A threaded comment which must be associated with an instance of
    ``django.contrib.auth.models.User``.  It is given its hierarchy by a
    nullable relationship back on itself named ``parent``.

    This ``ThreadedComment`` supports several kinds of markup languages,
    including Textile, Markdown, and ReST.

    It also includes two Managers: ``objects``, which is the same as the normal
    ``objects`` Manager with a few added utility functions (see above), and
    ``public``, which has those same utility functions but limits the QuerySet to
    only those values which are designated as public (``is_public=True``).

    """

    # Generic Foreign Key Fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(_("object ID"))
    content_object = GenericForeignKey()

    # Hierarchy Field
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        default=None,
        related_name="children",
        on_delete=models.CASCADE,
    )

    # User Field
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Date Fields
    date_submitted = models.DateTimeField(
        _("date/time submitted"), default=datetime.now
    )
    date_modified = models.DateTimeField(_("date/time modified"), default=datetime.now)
    date_approved = models.DateTimeField(
        _("date/time approved"), default=None, null=True, blank=True
    )

    # Meat n' Potatoes
    comment = models.TextField(_("comment"))
    markup = models.IntegerField(
        choices=MARKUP_CHOICES, default=DEFAULT_MARKUP, null=True, blank=True
    )

    # Status Fields
    is_public = models.BooleanField(_("is public"), default=True)
    is_approved = models.BooleanField(_("is approved"), default=False)

    objects = ThreadedCommentManager()
    public = PublicThreadedCommentManager()

    def __str__(self):
        if len(self.comment) > 50:
            return self.comment[:50] + "..."
        return self.comment[:50]

    def save(self, **kwargs):
        if not self.markup:
            self.markup = DEFAULT_MARKUP
        self.date_modified = datetime.now()
        if not self.date_approved and self.is_approved:
            self.date_approved = datetime.now()
        super(ThreadedComment, self).save(**kwargs)

    def get_content_object(self):
        """Wrapper around the GenericForeignKey due to compatibility reasons
        and due to ``list_display`` limitations."""
        return self.content_object

    class Meta:
        ordering = ("-date_submitted",)
        verbose_name = _("Threaded Comment")
        verbose_name_plural = _("Threaded Comments")
        get_latest_by = "date_submitted"
