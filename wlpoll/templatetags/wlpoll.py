#!/usr/bin/env python -tt
# encoding: utf-8
#

from widelands.wlpoll.models import Choice, Poll
from django import template
from urllib import urlencode, quote

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

        data = ',\n'.join("[ '%s', %i ]" % (c.choice.replace("'", "\\'"), c.votes) for c in choices)

        s = r"""
        <script type="text/javascript">
        var chart1; // globally available
        $(document).ready(function() {
              chart1 = new Highcharts.Chart({
                 chart: {
                    renderTo: 'chartContainer',
                    type: 'pie'
                 },
                 title: {
                    text: '%(name)s'
                 },
                 tooltip: {
                     formatter: function() {
                        return '<b>'+ this.y +' votes</b>: '+ this.percentage +' %%';
                     }
                  },
                 series: [{
                    type: 'pie',
                    data: [
                        %(data)s
                    ],
                 },
                 ]
              });
           });
       </script>

        <div id="chartContainer" style="width: 100%%; height: 400px"></div>
        """ % { "name": p.name, "data": data }

        return s

def do_display_poll( parser, token):
    try:
        tag_name,poll_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]

    return DisplayPollNode(poll_var)


class GetOpenPolls(template.Node):
    def __init__(self, varname):
        self._vn = varname

    def render(self,context):
        """
        Only has side effects
        """
        context[self._vn] = Poll.objects.open()
        return ""

def do_get_open_polls( parser, token ):
    try:
        tag_name,as_name,variable = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "required: %r as <variable name>" % token.contents.split()[0]

    return GetOpenPolls(variable)

register.tag('display_poll',do_display_poll)
register.tag('get_open_polls',do_get_open_polls)

