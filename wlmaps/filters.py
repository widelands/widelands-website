import django_filters

from . import models


class MapFilter(django_filters.FilterSet):
    nr_players = django_filters.RangeFilter()
    w = django_filters.RangeFilter()
    h = django_filters.RangeFilter()
    wl_version_after = django_filters.NumberFilter(label='Max required version', lookup_expr='lt')
    o = django_filters.OrderingFilter(
        fields=('pub_date', 'name', 'author', 'w', 'h', 'ratings__average'),
        field_labels={
            'pub_date': 'Upload date',
            'w': 'Width',
            'h': 'Height',
            'ratings__average': 'Average rating',
        }
    )

    class Meta:
        model = models.Map
        fields = {
            'name': ['icontains'],
            'author': ['iexact'],
        }
