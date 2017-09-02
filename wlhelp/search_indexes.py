from haystack import indexes
from wlhelp.models import Worker


class WorkerIndex(indexes.SearchIndex, indexes.Indexable):

    """Create a search index. Changes made here need to be reindexed. Defined
    fields are stored in the index, so when displaying the result the data is
    read from the index and do not hit the database.

    Except the 'text' field all defined fields will be in the index.

    'text' indicates the template where the concatenated data
           is gathered and the search runs over.

    """

    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    displayname = indexes.CharField(model_attr='displayname')
    help = indexes.CharField(model_attr='help')

    def get_model(self):
        return Worker
