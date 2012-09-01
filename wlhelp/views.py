from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from .models import Worker, Ware, Building, Tribe

from settings import WIDELANDS_SVN_DIR, MEDIA_ROOT
import os

def index( request ):
    tribes = Tribe.objects.all().order_by("displayname")

    return render_to_response('wlhelp/index.html',
        context_instance=RequestContext(request,
        { "tribes": tribes }))

def tribe_details( request, tribe ):
    t = get_object_or_404(Tribe, name=tribe)

    return render_to_response('wlhelp/tribe_details.html',
        context_instance=RequestContext(request,
        { "tribe": t }))

def ware_details( request, tribe, ware ):
    w = get_object_or_404(Ware,tribe__name=tribe,name=ware)
    t = Tribe.objects.get(name=tribe)

    return render_to_response('wlhelp/ware_details.html', 
        context_instance=RequestContext(request, 
        { "ware": w, "tribe": t }))

def building_details( request, tribe, building ):
    b = get_object_or_404(Building,tribe__name=tribe,name=building)
    t = Tribe.objects.get(name=tribe)

    return render_to_response('wlhelp/building_details.html', 
        context_instance=RequestContext(request, 
        { "building": b, "tribe": t }))

def worker_details( request, tribe, worker ):
    w = get_object_or_404(Worker,tribe__name=tribe,name=worker)
    t = Tribe.objects.get(name=tribe)

    return render_to_response('wlhelp/worker_details.html', 
        context_instance=RequestContext(request, 
        { "worker": w, "tribe": t }))

def workers(request, tribe="barbarians"):
    t = get_object_or_404(Tribe,name=tribe)
    return render_to_response('wlhelp/workers.html', context_instance=RequestContext(request, 
        { "workers": Worker.objects.filter(tribe=t).order_by("displayname"),
          "tribe": t }))

def wares(request, tribe="barbarians"):
    t = get_object_or_404(Tribe,name=tribe)
    return render_to_response('wlhelp/wares.html', context_instance=RequestContext(request, 
        { "wares": Ware.objects.filter(tribe=t).order_by("displayname"),
          "tribe": t }))

def buildings(request, tribe="barbarians"):
    t = get_object_or_404(Tribe,name=tribe)

    # Request all the objects
    buildings = {}

    buildings["headquarters"] = Building.objects.filter(tribe=t,name="headquarters").order_by("displayname")
    
    all = Building.objects.filter(tribe=t).exclude(name="headquarters")
    
    # Now, all small buildings
    small = all.filter(size="S",tribe=t).order_by("displayname")
    buildings["small"] = small.filter(enhanced_from=None)
    buildings["small_enhanced"] = small.exclude(enhanced_from=None)
    
    # Now, all medium buildings
    medium = all.filter(size="M",tribe=t).order_by("displayname")
    buildings["medium"] = medium.filter(enhanced_from=None)
    buildings["medium_enhanced"] = medium.exclude(enhanced_from=None)

    # Now, all big buildings
    big = all.filter(size="B",tribe=t).order_by("displayname")
    buildings["big"] = big.filter(enhanced_from=None)
    buildings["big_enhanced"] = big.exclude(enhanced_from=None)
    
    # Now, all mines
    mine = all.filter(size="I",tribe=t).order_by("displayname")
    buildings["mine"] = mine.filter(enhanced_from=None)
    buildings["mine_enhanced"] = mine.exclude(enhanced_from=None)

    # Now, all ports
    port = all.filter(size="P",tribe=t).order_by("displayname")
    buildings["port"] = port.filter(enhanced_from=None)
    buildings["port_enhanced"] = port.exclude(enhanced_from=None)

    return render_to_response('wlhelp/buildings.html', context_instance=RequestContext(request, 
        { "buildings": buildings, "tribe": t }))


