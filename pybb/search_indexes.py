from haystack import indexes
from pybb.models import Topic, Post


class TopicIndex(indexes.SearchIndex, indexes.Indexable):

    """Create a search index. Changes made here need to be reindexed. Defined
    fields are stored in the index, so when displaying the result the data is
    read from the index and do not hit the database.

    Except the 'text' field all defined fields will be in the index.

    'text' indicates the template where the concatenated data
           is gathered and the search runs over.

    'date' is the field which is used for sorting

    """

    text = indexes.CharField(document=True, use_template=True)
    date = indexes.DateTimeField(model_attr='created')
    name = indexes.CharField(model_attr='name')
    # Following fields get stored in the index but are not be used for indexing
    # This avoids hitting the database when the results are rendered
    user = indexes.CharField(model_attr='user', indexed=False)
    topic_link = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def get_model(self):
        return Topic

    def index_queryset(self, using=None):
        """Do not index hidden topics."""
        return self.get_model().objects.filter(forum__category__internal=False).exclude(posts__hidden=True)

    def get_updated_field(self):
        return 'updated'


class PostIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    date = indexes.DateTimeField(model_attr='created')
    body_text = indexes.CharField(model_attr='body_text')
    # Following fields get stored in the index but are not be used for indexing
    # This avoids hitting the database when the results are rendered
    user = indexes.CharField(model_attr='user', indexed='false')
    post_link = indexes.CharField(
        model_attr='get_absolute_url', indexed='false')

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        """Do not index hidden posts."""
        return self.get_model().objects.filter(topic__forum__category__internal=False).exclude(hidden=True)

    def get_updated_field(self):
        return 'created'
