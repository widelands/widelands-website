#!/usr/bin/env python -tt
# encoding: utf-8
#

from widelands.wlpoll.models import Choice, Poll
from django import template
from urllib import urlencode

register = template.Library()

class DisplayPollNode(template.Node):
    def __init__(self, poll_var):
        self._poll = template.Variable(poll_var)

    def render(self,context):
        """
        Render this chart using googles chart API.
        """
        p = self._poll.resolve(context)

        choices = p.choices.all()
        label = '|'.join([ c.choice for c in choices[::-1] ])
        counts = [ c.votes for c in choices ]
        allvotes = float(sum(counts))
        countstr = '|'.join([ ("t  %.1f %% (%i),000000,0,%i,11" % (c.votes*100/allvotes,c.votes,idx)) 
                            for idx,c in enumerate(choices) ])
        
        args = (
         ("cht","bhs"),                             # Chart type
         ("chs", "800x200"),                        # Chart size
         ("chd", 't:' + ','.join(map(str,counts))), # Chart data
         ("chds", '0,%i' % max(counts)),            # Data scaling
         ("chxt", "y"),
         ("chxs", "0,d0dfff,13"),                   # Label colors & size
         ("chco", "ccaf7a"),                        # Chart colors
         ("chxl", "0:|" + label + "|"),             # Label on data sets
         ("chm", countstr ),                        # Text labels on the right side of the data sets
         
         ("chf", "bg,s,ffffff00" ),    # Solid fill the background with transparent black 
         ("chma", "0,15,0,0" ),    # Chart margins 
         ("chba", "a"),            # Resize bars automatically
        )
        url = "http://chart.apis.google.com/chart?" + urlencode(args)
        
        # chd=t:60,40,80,90&chs=620x140&chxt=y&chxl=0:|Hallo%20Du%20welt|Welt|Wie|gehts|&chm=t%20%2022.6%,000000,0,0,11
        return """<img src="%s" alt="GoogleChart" class="googleChart"/>""" % url

def do_display_poll( parser, token):
    try:
        tag_name,poll_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0] 

    return DisplayPollNode(poll_var)

register.tag('display_poll',do_display_poll)

