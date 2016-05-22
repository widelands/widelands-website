from django.db import models

import settings
if settings.USE_SPHINX:
    from djangosphinx.models import SphinxSearch


class Tribe(models.Model):
    name = models.CharField(max_length=100)
    displayname = models.CharField(max_length=100)
    descr = models.TextField()
    icon_url = models.CharField(max_length=256)
    network_pdf_url = models.CharField(max_length=256)
    network_gif_url = models.CharField(max_length=256)


class Worker(models.Model):
    if settings.USE_SPHINX:
        search = SphinxSearch(
            weights={
                'displayname': 100,
                'help': 60,
                'name': 20,
            }
        )

    name = models.CharField(max_length=100)
    displayname = models.CharField(max_length=100)
    tribe = models.ForeignKey(Tribe)
    # URL to include this, i wasn't able to feed django local images
    image_url = models.CharField(max_length=256)
    graph_url = models.CharField(max_length=256)  # URL to the help graph
    imagemap = models.TextField()  # the image map for the help graph

    # This limit shall probably cover the longest help (found 209, nothing
    # more)
    help = models.TextField(max_length=256)
    exp = models.TextField(max_length=8)  # Just in case
    becomes = models.OneToOneField(
        'self', related_name='trained_by_experience', blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.name


class Ware(models.Model):
    name = models.CharField(max_length=100)
    displayname = models.CharField(max_length=100)
    tribe = models.ForeignKey(Tribe)
    # URL to include this, i wasn't able to feed django local images
    image_url = models.CharField(max_length=256)
    graph_url = models.CharField(max_length=256)  # URL to the help graph
    imagemap = models.TextField()  # the image map for the help graph

    # This limit shall probably cover the longest help (found 209, nothing
    # more)
    help = models.TextField(max_length=256)

    if settings.USE_SPHINX:
        search = SphinxSearch(
            weights={
                'displayname': 100,
                'help': 60,
                'name': 20,
            }
        )

    def __unicode__(self):
        return u'%s' % self.name


class BuildingManager(models.Manager):

    def small(self):
        return self.all().filter(size='S')

    def medium(self):
        return self.all().filter(size='M')

    def big(self):
        return self.all().filter(size='B')

    def mine(self):
        return self.all().filter(size='I')

    def port(self):
        return self.all().filter(size='P')

    def headquarters(self):
        return self.all().filter(size='H')

        # return self.build_wares.count()

    pass


class Building(models.Model):
    SIZES = (
            ('S', 'small'),
            ('M', 'medium'),
            ('B', 'big'),
            ('I', 'mine'),
            ('P', 'port'),
            ('H', 'headquarters'),
    )
    TYPES = (
            ('P', 'productionsite'),
            ('W', 'warehouse'),
            ('M', 'militarysite'),
            ('T', 'trainingsite')
    )

    objects = BuildingManager()

    if settings.USE_SPHINX:
        search = SphinxSearch(
            weights={
                'displayname': 100,
                'help': 60,
                'name': 20,
            }
        )

    name = models.CharField(max_length=100)
    displayname = models.CharField(max_length=100)
    tribe = models.ForeignKey(Tribe)
    # URL to include this, i wasn't able to feed django local images
    image_url = models.CharField(max_length=256)
    graph_url = models.CharField(max_length=256)  # URL to the help graph
    imagemap = models.TextField()  # the image map for the help graph

    size = models.CharField(max_length=1, choices=SIZES)
    type = models.CharField(max_length=1, choices=TYPES)  # productionsite...

    help = models.TextField(blank=True)

    # Enhances to
    enhancement = models.OneToOneField(
        'self', related_name='enhanced_from', blank=True, null=True)

    # Build cost
    build_wares = models.ManyToManyField(
        Ware, related_name='build_ware_for_buildings', blank=True)
    # ' '.joined() integer strings
    build_costs = models.CharField(max_length=100, blank=True)

    # Workers
    workers_types = models.ManyToManyField(
        Worker, related_name='workers_for_buildings', blank=True)
    # ' '.joined() integer strings
    workers_count = models.CharField(max_length=100, blank=True)

    # Store
    store_wares = models.ManyToManyField(
        Ware, related_name='stored_ware_for_buildings', blank=True)
    # ' '.joined() integer strings
    store_count = models.CharField(max_length=100, blank=True)

    # Output
    output_wares = models.ManyToManyField(
        Ware, related_name='produced_by_buildings', blank=True)
    output_workers = models.ManyToManyField(
        Worker, related_name='trained_by_buildings', blank=True)

    def save(self, *args, **kwargs):

        tdict = dict((b, a) for a, b in self.TYPES)
        sdict = dict((b, a) for a, b in self.SIZES)

        self.type = tdict.get(self.type, self.type)
        self.size = sdict.get(self.size, self.size)

        return models.Model.save(self, *args, **kwargs)

    def has_build_cost(self):
        return (self.build_wares.all().count() != 0)

    def get_build_cost(self):
        count = map(int, self.build_costs.split())
        for c, w in zip(count, self.build_wares.all()):
            yield [w] * c

    def has_workers(self):
        return (self.workers_types.all().count() != 0)

    def get_workers(self):
        count = map(int, self.workers_count.split())
        for c, wor in zip(count, self.workers_types.all()):
            yield [wor] * c

    def produces(self):
        return (self.output_wares.all().count() != 0)

    def get_ware_outputs(self):
        return self.output_wares.all()

    def trains(self):
        return (self.output_workers.all().count() != 0)

    def get_worker_outputs(self):
        return self.output_workers.all()

    def has_outputs(self):
        return (self.output_workers.all().count() != 0 or self.output_wares.all().count() != 0)

    def has_stored_wares(self):
        return (self.store_wares.all().count() != 0)

    def get_stored_wares(self):
        count = map(int, self.store_count.split())
        for c, w in zip(count, self.store_wares.all()):
            yield [w] * c

    def __unicode__(self):
        return u"%s/%s" % (self.tribe.name, self.name)
