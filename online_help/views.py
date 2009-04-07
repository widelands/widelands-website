from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from .models import Ware, Building, Tribe


import pydot
from settings import WIDELANDS_SVN_DIR, MEDIA_URL, MEDIA_ROOT
import os

def _add_building_node( d, b ):
    table = """<<table cellborder="0" border="0">
<tr>
  <td><IMG SRC="%s/%s" /></td>
  <td>%s</td>
</tr>
</table>>""" % (MEDIA_ROOT, b.image_url, b.displayname)
    table = table.replace('//','/')
    
    print "b.image_url:", b.image_url

    if b.type == 'M':
        fillcolor = '#000000e2'
    elif b.type == 'P':
        fillcolor = 'orange' 
    elif b.type == 'T':
        fillcolor = '#ff00ffe2'
    elif b.type == 'W':
        fillcolor = 'blue'
    else:
        print b.type

    url = "/help/%s/buildings/%s/" % (b.tribe.name, b.name )
    n = pydot.Node( b.name, shape = 'rect', label = table, URL = url, fillcolor=fillcolor, style="filled"   ) 
    d.add_node( n )

def _add_ware_node( d, w ):
    table = """<<table cellborder="0" border="0">
<tr>
<td><IMG SRC="%s/%s" /></td>
<td><font point-size="24">%s</font></td>
</tr>
</table>>""" % (MEDIA_ROOT, w.image_url, w.displayname)
    n = pydot.Node( w.name, shape = 'rectangle', label = table  ) 
    d.add_node( n )

print 'contains ipython embed code!'
from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed()

def _make_ware_graph( w ):
    d = pydot.Dot()
    d.set_name(w.name + "_graph")
    
    d.set_dpi("100")
    d.set_size("6,1000")
    #d.set_ratio("compress")
    #d.set_fontsize("48pt")

    _add_ware_node( d, w )

    producers = w.produced_by_buildings.all()
    for p in producers:
        _add_building_node( d, p )
        e = pydot.Edge( p.name, w.name, color = "green"  )
        d.add_edge( e )
    
    # Consumed by
    for p in w.stored_ware_for_buildings.all():
        _add_building_node( d, p )
        e = pydot.Edge( w.name, p.name, color ="red" )
        d.add_edge( e )

    # Needed for build off
    # for p in w.build_ware_for_buildings.all():
        # _add_building_node( d, p )
    #     e = pydot.Edge( w.name, p.name, color ="yellow" )
    #     d.add_edge( e )
    # d.set_dpi('100')
    # d.set_size( '20,15')

    d.set_bgcolor("transparent")
    #d.set_rankdir("LR")
    
    return d

def _make_building_graph( b ):
    d = pydot.Dot()
    d.set_name(b.name + "_graph")
    
    d.set_dpi("100")
    d.set_size("6,1000")
    #d.set_ratio("compress")
    #d.set_fontsize("48pt")

    
    # Produces
    for w in b.output_wares.all():
        _add_ware_node( d, w )
        e = pydot.Edge( b.name, w.name, color = "green", samehead="True", sametail="True",
            constraint="False", tailport="s", headport="s")
        d.add_edge( e )
    
    _add_building_node( d, b )

    # Consumes 
    # for w in b.store_wares.all():
    #     _add_ware_node( d, w )
    #     e = pydot.Edge( w.name, b.name, color = "red", samehead="True", sametail="True",
    #             constraint="False", headport="w")
    #     d.add_edge( e )
    
    # Enhancements 
    try:
        _add_building_node( d, b.enhancement )
        e = pydot.Edge( b.name, b.enhancement.name, color = "blue", weight="20"  )
        #d.add_edge( e )
    except:
        pass
    try:
        _add_building_node( d, b.enhanced_from )
        e = pydot.Edge( b.enhanced_from.name, b.name, color = "blue", weight="20"  )
        #d.add_edge( e )
    except:
        pass

    
    d.set_root(b.name)
    d.set_margin("0.,0.")
    d.set_nodesep("0.12")
    d.set_ranksep("0.32")
    d.set_ordering("out") 
    # Needed for build off
    # for p in w.build_ware_for_buildings.all():
        # _add_building_node( d, p )
    #     e = pydot.Edge( w.name, p.name, color ="yellow" )
    #     d.add_edge( e )
    # d.set_dpi('100')
    # d.set_size( '20,15')

    d.set_bgcolor("transparent")
    #d.set_rankdir("LR")
    
    return d

def ware_graph( request, tribe, ware):
    w = get_object_or_404(Ware,tribe__name=tribe,name=ware)
    
    d = _make_ware_graph( w )
    svg = d.create_png(prog="dot")

    # ipshell()
    #svg = svg.replace(MEDIA_ROOT, MEDIA_URL)
   
    #return HttpResponse( svg, mimetype="image/svg+xml")
    return HttpResponse( svg, mimetype="image/png")

def building_graph( request, tribe, building):
    b = get_object_or_404(Building,tribe__name=tribe,name=building)
    
    d = _make_building_graph( b )
    svg = d.create_png(prog="dot")

    # ipshell()
    #svg = svg.replace(MEDIA_ROOT, MEDIA_URL)
   
    #return HttpResponse( svg, mimetype="image/svg+xml")
    d.write_dot("file.dot")
    return HttpResponse( svg, mimetype="image/png")


def ware_details( request, tribe, ware ):
    w = get_object_or_404(Ware,tribe__name=tribe,name=ware)
    
    d = _make_ware_graph( w )
    svg = d.create_cmapx()

    return render_to_response('ware_details.html', 
        context_instance=RequestContext(request, 
        { "ware": w , 
          "map": svg,}))

def building_details( request, tribe, building ):
    b = get_object_or_404(Building,tribe__name=tribe,name=building)
    
    d = _make_building_graph( b )
    svg = d.create_cmapx()

    return render_to_response('building_details.html', 
        context_instance=RequestContext(request, 
        { "building": b , 
          "map": svg,}))

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


