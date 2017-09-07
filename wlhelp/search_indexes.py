from haystack import indexes
from wlhelp.models import Worker, Ware, Building, Tribe
from haystack.fields import DateField
from datetime import date


class WorkerIndex(indexes.SearchIndex, indexes.Indexable):

    """Create a search index. Changes made here need to be reindexed. Defined
    fields are stored in the index, so when displaying the result the data is
    read from the index and do not hit the database.

    Except the 'text' field all defined fields will be in the index.

    'text' indicates the template where the concatenated data
           is gathered and the search runs over.

    """

    text = indexes.CharField(document=True, use_template=True)
    # To get date related search working: 
    date = DateField(default=date.today())
    displayname = indexes.CharField(model_attr='displayname')
    help = indexes.CharField(model_attr='help')

    def get_model(self):
        return Worker

class WareIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    # To get date related search working: 
    date = DateField(default=date.today())
    displayname = indexes.CharField(model_attr='displayname')
    help = indexes.CharField(model_attr='help')

    def get_model(self):
        return Ware

class BuildingIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    # To get date related search working: 
    date = DateField(default=date.today())
    displayname = indexes.CharField(model_attr='displayname')
    help = indexes.CharField(model_attr='help')

    def get_model(self):
        return Building

class TribeIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    # To get date related search working: 
    date = DateField(default=date.today())
    displayname = indexes.CharField(model_attr='displayname')
    help = indexes.CharField(model_attr='descr')

    def get_model(self):
        return Tribe