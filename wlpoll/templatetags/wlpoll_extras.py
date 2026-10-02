#!/usr/bin/env python -tt
# encoding: utf-8
#

from wlpoll.models import Poll
from django import template
from django.utils.html import json_script

register = template.Library()


class DisplayPollNode(template.Node):
    def __init__(self, poll_var):
        self._poll = template.Variable(poll_var)

    def render(self, context):
        """Render this Poll using Highcharts"""
        p = self._poll.resolve(context)

        # Pass the poll as JSON data block, so that names and choices can't
        # break out of the JavaScript strings or the <script> element
        poll_data = json_script(
            {
                "name": p.name,
                "choices": [[c.choice, c.votes] for c in p.choices.all()],
            },
            "pollData",
        )

        s = rf"""
        {poll_data}
        <script type="text/javascript">
        $(document).ready(function() {{
              const poll = JSON.parse(document.getElementById('pollData').textContent);
              Highcharts.chart('chartContainer', {{
                 chart: {{
                    type: 'pie'
                 }},
                 plotOptions: {{
                    pie: {{
                        center: ["50%", "50%"],
                        dataLabels: {{
                            style: {{
                                width: '150px',
                            }}
                        }}
                    }}
                 }},
                 title: {{
                    text: poll.name
                 }},
                 tooltip: {{
                     formatter: function() {{
                        return '<b>'+ this.y +' votes</b>: '+ this.percentage +' %';
                     }}
                  }},
                 series: [{{
                    type: 'pie',
                    data: poll.choices,
                 }},
                 ]
              }});
           }});
       </script>
        """

        return s


def do_display_poll(parser, token):
    try:
        tag_name, poll_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            f"{token.contents.split()[0]!r} tag requires a single argument"
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
            f"required: {token.contents.split()[0]!r} as <variable name>"
        )

    return GetOpenPolls(variable)


register.tag("display_poll", do_display_poll)
register.tag("get_open_polls", do_get_open_polls)
