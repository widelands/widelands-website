import django_filters

from . import models


VERSION_CHOICES = (
    ('', 'any'),
    ('19', 'build 19 or newer'),
    ('20', 'build 20 or newer'),
    ('21', 'dev'),
)


class MapFilter(django_filters.FilterSet):
    nr_players = django_filters.RangeFilter()
    w = django_filters.RangeFilter()
    h = django_filters.RangeFilter()
    o = django_filters.OrderingFilter(
        fields=('pub_date', 'name', 'author', 'w', 'h', 'ratings__average', 'nr_downloads'),
        field_labels={
            'pub_date': 'Upload date',
            'w': 'Width',
            'h': 'Height',
            'ratings__average': 'Average rating',
            'nr_downloads': 'Downloads',
        }
    )

    class Meta:
        model = models.Map
        fields = {
            'name': ['icontains'],
            'author': ['iexact'],
        }
