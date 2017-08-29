import datetime
from haystack import indexes
from pybb.models import Topic, Post


class TopicIndex(indexes.SearchIndex, indexes.Indexable):

    """Create a search index. Changes made here need to be reindexed.
    Defined fields are stored in the index, so when displaying the result the
    data is read from the index and do not hit the database.

    Except the 'text' field all defined fields will be in the index.

    'text' indicates the template where the concatenated data
           is gathered and the search runs over.

    'date' is the field which is used for sorting

    """

    text = indexes.CharField(document=True, use_template=True)
    date = indexes.DateTimeField(model_attr='created')
    name = indexes.CharField(model_attr='name')

    def get_model(self):
        return Topic

    def get_updated_field(self):
        return "updated"

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
    date = indexes.DateTimeField(model_attr='created')
    body_text = indexes.CharField(model_attr='body_text')

    def get_model(self):
        return Post
    
    def get_updated_field(self):
        return "created"
