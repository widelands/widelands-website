from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from .models import Worker, Ware, Building, Tribe


def index(request):
    tribes = Tribe.objects.all().order_by('displayname')

    return render(request, 'wlhelp/index.html',
                  {'tribes': tribes, })


def ware_details(request, tribe, ware):
    w = get_object_or_404(Ware, tribe__name=tribe, name=ware)
    t = Tribe.objects.get(name=tribe)

    return render(request, 'wlhelp/ware_details.html',
                  {'ware': w,
                   'tribe': t, })


def building_details(request, tribe, building):
    b = get_object_or_404(Building, tribe__name=tribe, name=building)
    t = Tribe.objects.get(name=tribe)

    return render(request, 'wlhelp/building_details.html',
                  {'building': b,
                   'tribe': t, })


def worker_details(request, tribe, worker):
    w = get_object_or_404(Worker, tribe__name=tribe, name=worker)
    t = Tribe.objects.get(name=tribe)

    return render(request, 'wlhelp/worker_details.html',
                  {'worker': w,
                   'tribe': t, })


def workers(request, tribe='barbarians'):
    t = get_object_or_404(Tribe, name=tribe)
    return render(request, 'wlhelp/workers.html',
                  {'workers': Worker.objects.filter(tribe=t).order_by('displayname'),
                   'tribe': t, })


def wares(request, tribe='barbarians'):
    t = get_object_or_404(Tribe, name=tribe)
    return render(request, 'wlhelp/wares.html',
                  {'wares': Ware.objects.filter(tribe=t).order_by('displayname'),
                   'tribe': t, })


def buildings(request, tribe='barbarians'):
    t = get_object_or_404(Tribe, name=tribe)

    # Request all the objects
    buildings = {}

    # All headquarters
    buildings['headquarters'] = Building.objects.filter(
        size='H', tribe=t).order_by('displayname')

    # Now, all small buildings
    small = Building.objects.filter(size='S', tribe=t).order_by('displayname')
    buildings['small'] = small.filter(enhanced_from=None)
    buildings['small_enhanced'] = small.exclude(enhanced_from=None)

    # Now, all medium buildings
    medium = Building.objects.filter(size='M', tribe=t).order_by('displayname')
    buildings['medium'] = medium.filter(enhanced_from=None)
    buildings['medium_enhanced'] = medium.exclude(enhanced_from=None)

    # Now, all big buildings
    big = Building.objects.filter(size='B', tribe=t).order_by('displayname')
    buildings['big'] = big.filter(enhanced_from=None)
    buildings['big_enhanced'] = big.exclude(enhanced_from=None)

    # Now, all mines
    mine = Building.objects.filter(size='I', tribe=t).order_by('displayname')
    buildings['mine'] = mine.filter(enhanced_from=None)
    buildings['mine_enhanced'] = mine.exclude(enhanced_from=None)

    # Now, all ports
    port = Building.objects.filter(size='P', tribe=t).order_by('displayname')
    buildings['port'] = port.filter(enhanced_from=None)
    buildings['port_enhanced'] = port.exclude(enhanced_from=None)

    return render(request, 'wlhelp/buildings.html',
                  {'buildings': buildings,
                   'tribe': t, })
