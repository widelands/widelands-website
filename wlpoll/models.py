from django.db import models
import datetime

class PollManager(models.Manager):
    def open(self):
        return self.all().exclude(closed_date__lte=datetime.datetime.now)

class Poll(models.Model):
    name = models.CharField(max_length=256)
    pub_date = models.DateTimeField("date published", default = datetime.datetime.now)
    closed_date = models.DateTimeField("date closed", default= lambda: datetime.datetime.now() + datetime.timedelta(days=90), 
                            blank=True, null=True)
    
    objects = PollManager()

    def total_votes(self):
        return self.choices.all().aggregate(models.Sum("votes"))["votes__sum"]
    
    def is_closed(self):
        if self.closed_date is None:
            return False
        return self.closed_date < datetime.datetime.now()
    
    @models.permalink
    def get_absolute_url(self):
        return ('wlpoll_detail', None, {'object_id': self.id})

    def __unicode__(self):
        return self.name

class Choice(models.Model):
    poll = models.ForeignKey(Poll, related_name="choices")
    choice = models.CharField(max_length=256)
    votes = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return u"%i:%s" % (self.votes,self.choice)
