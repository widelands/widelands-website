from haystack import indexes
from news.models import Post
import datetime


class PostIndex(indexes.SearchIndex, indexes.Indexable):

    """Create a search index. Changes made here need to be reindexed.
    Defined fields are stored in the index, so when displaying the result the
    data is read from the index and do not hit the database.

    Except the 'text' field all defined fields will be in the index.

    'text' indicates the template where the concatenated data
           is gathered and the search runs over.

    'date' is the field which is used for sorting

    """

    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr="title")
    body = indexes.CharField(model_attr="body")
    date = indexes.DateTimeField(model_attr="publish")

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        "Don't index news of the future"
        return self.get_model().objects.filter(publish__lte=datetime.datetime.now())

    def get_updated_field(self):
        return "created"
