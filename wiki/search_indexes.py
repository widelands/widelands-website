from haystack import indexes
from wiki.models import Article
from haystack.fields import DateField
from datetime import date


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    """Create a search index. Changes made here need to be reindexed. Defined
    fields are stored in the index, so when displaying the result the data is
    read from the index and do not hit the database.

    Except the 'text' field all defined fields will be in the index.

    'text' indicates the template where the concatenated data
           is gathered and the search runs over.

    'date' is the field which is used for sorting

    """

    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr="title")
    summary = indexes.CharField(model_attr="summary", null=True)
    content = indexes.CharField(model_attr="content")
    # To get date related search working
    # we assume the index is always up to date
    date = DateField(default=date.today())

    def get_model(self):
        return Article

    def get_updated_field(self):
        return "last_update"
