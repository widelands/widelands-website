from haystack import indexes
from haystack.fields import DateField
from wlmaps.models import Map
from datetime import date


class MapIndex(indexes.SearchIndex, indexes.Indexable):
    """Create a search index. Changes made here need to be reindexed.
    Defined fields are stored in the index, so when displaying the result the
    data is read from the index and do not hit the database.

    Except the 'text' field all defined fields will be in the index.

    'text' indicates the template where the concatenated data
           is gathered and the search runs over.

    'date' is the field which is used for sorting

    """

    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr="author")
    date = DateField(default=date.today())
    pub_date = indexes.DateTimeField(model_attr="pub_date")

    def get_model(self):
        return Map

    def get_updated_field(self):
        return "pub_date"
