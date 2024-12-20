#!/usr/bin/env python -tt
# encoding: utf-8
#

from wlpoll.models import Choice, Poll
from django import template
from urllib.parse import urlencode, quote

register = template.Library()


class DisplayPollNode(template.Node):
    def __init__(self, poll_var):
        self._poll = template.Variable(poll_var)

    def render(self, context):
        """Render this Poll using Highcharts"""
        p = self._poll.resolve(context)

        choices = p.choices.all()

        _esc = lambda s: s.replace("'", "\\'")

        data = ",\n".join("[ '%s', %i ]" % (_esc(c.choice), c.votes) for c in choices)

        s = r"""
        <script type="text/javascript">
        $(document).ready(function() {
              Highcharts.chart('chartContainer', {
                 chart: {
                    type: 'pie'
                 },
                 plotOptions: {
                    pie: {
                        center: ["50%%", "50%%"],
                        dataLabels: {
                            style: {
                                width: '150px',
                            }
                        }
                    } 
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
        """ % {
            "name": _esc(p.name),
            "data": data,
        }

        return s


def do_display_poll(parser, token):
    try:
        tag_name, poll_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0]
        )

    return DisplayPollNode(poll_var)


class GetOpenPolls(template.Node):
    def __init__(self, varname):
        self._vn = varname

    def render(self, context):
        """Only has side effects."""
        if "user" in context:
            user = context["user"]
            rv = []
            for p in Poll.objects.open():
                p.user_has_voted = (
                    False if user.is_anonymous else p.has_user_voted(user)
                )
                rv.append(p)
            context[self._vn] = rv
        return ""


def do_get_open_polls(parser, token):
    try:
        tag_name, as_name, variable = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "required: %r as <variable name>" % token.contents.split()[0]
        )

    return GetOpenPolls(variable)


register.tag("display_poll", do_display_poll)
register.tag("get_open_polls", do_get_open_polls)
