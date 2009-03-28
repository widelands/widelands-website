from django.db import models
import datetime

class Poll(models.Model):
    name = models.CharField(max_length=256)
    pub_date = models.DateTimeField("date published", default = datetime.datetime.now)
    closed_date = models.DateTimeField("date closed", blank=True, null=True)

    def total_votes(self):
        return self.choices.all().aggregate(models.Sum("votes"))["votes__sum"]

    def __unicode__(self):
        return self.name

class Choice(models.Model):
    poll = models.ForeignKey(Poll, related_name="choices")
    choice = models.CharField(max_length=256)
    votes = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return u"%i:%s" % (self.votes,self.choice)
