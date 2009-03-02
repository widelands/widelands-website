from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from .models import Ware, Building, Tribe

def wares(request, tribe="barbarians"):
    t = get_object_or_404(Tribe,name=tribe)
    return render_to_response('wares.html', context_instance=RequestContext(request, 
        { "wares": Ware.objects.filter(tribe=t) }))

def buildings(request, tribe="barbarians"):
    t = get_object_or_404(Tribe,name=tribe)

    # Request all the objects
    buildings = {}

    buildings["headquarters"] = Building.objects.get(tribe=t,name="headquarters") 
    
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
    
    # Now, all mines buildings
    mine = all.filter(size="I",tribe=t).order_by("displayname")
    buildings["mine"] = mine.filter(enhanced_from=None)
    buildings["mine_enhanced"] = mine.exclude(enhanced_from=None)

    return render_to_response('buildings.html', context_instance=RequestContext(request, 
        { "buildings": buildings }))


