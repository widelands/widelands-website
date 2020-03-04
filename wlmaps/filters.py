import django_filters

from . import models


class MapFilter(django_filters.FilterSet):
    nr_players = django_filters.RangeFilter()
    w = django_filters.RangeFilter()
    h = django_filters.RangeFilter()
    o = django_filters.OrderingFilter(
        fields=('pub_date', 'name', 'author', 'w', 'h'),
        field_labels={
            'pub_date': 'Upload date',
            'w': 'Width',
            'h': 'Height',
        }
    )

    class Meta:
        model = models.Map
        fields = {
            'name': ['icontains'],
            'author': ['iexact'],
        }
