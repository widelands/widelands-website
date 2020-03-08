import django_filters

from django.forms import widgets
from . import models


VERSION_CHOICES = (
    ('', 'any'),
    ('19', 'build 19 or newer'),
    ('20', 'build 20 or newer'),
    ('21', 'dev'),
)


class MapFilter(django_filters.FilterSet):
    uploader = django_filters.CharFilter(field_name='uploader__username', lookup_expr='iexact', label='Uploader')
    nr_players = django_filters.RangeFilter()
    w = django_filters.RangeFilter()
    h = django_filters.RangeFilter()
    o = django_filters.OrderingFilter(
        fields=('pub_date', 'w', 'h', 'ratings__average'),
        field_labels={
            'pub_date': 'Upload date',
            'w': 'Width',
            'h': 'Height',
            'ratings__average': 'Rating',
        }
    )

    class Meta:
        model = models.Map
        fields = {
            'name': ['icontains'],
            'author': ['iexact'],
        }
