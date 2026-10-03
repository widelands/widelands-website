from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Avg, Count, Sum
from django.utils.translation import gettext_lazy as _

from . import app_settings, get_star_ratings_rating_model_name


class RatingManager(models.Manager):
    def for_instance(self, instance):
        if isinstance(instance, self.model):
            raise TypeError(
                "Rating manager 'for_instance' expects model to be rated, not Rating model."
            )
        ct = ContentType.objects.get_for_model(instance)
        ratings, created = self.get_or_create(content_type=ct, object_id=instance.pk)
        return ratings

    def rate(self, instance, score, user):
        """Store or update the score of user for instance and return the Rating."""
        if isinstance(instance, self.model):
            raise TypeError(
                "Rating manager 'rate' expects model to be rated, not Rating model."
            )
        existing_rating = UserRating.objects.for_instance_by_user(instance, user)
        if existing_rating:
            existing_rating.score = score
            existing_rating.save()
            return existing_rating.rating

        rating = self.for_instance(instance)
        return UserRating.objects.create(user=user, score=score, rating=rating).rating


class AbstractBaseRating(models.Model):
    """
    Attaches Rating models and running counts to the model being rated via a generic relation.
    """

    count = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    average = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal(0.0))

    content_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    objects = RatingManager()

    class Meta:
        unique_together = ["content_type", "object_id"]
        abstract = True

    @property
    def percentage(self):
        return (self.average / app_settings.STAR_RATINGS_RANGE) * 100

    def to_dict(self):
        return {
            "count": self.count,
            "total": self.total,
            "average": self.average,
            "percentage": self.percentage,
        }

    def __str__(self):
        return "{}".format(self.content_object)

    def calculate(self):
        """
        Recalculate the totals, and save.
        """
        aggregates = self.user_ratings.aggregate(
            total=Sum("score"), average=Avg("score"), count=Count("score")
        )
        self.count = aggregates.get("count") or 0
        self.total = aggregates.get("total") or 0
        self.average = aggregates.get("average") or 0.0
        self.save()


class Rating(AbstractBaseRating):
    class Meta(AbstractBaseRating.Meta):
        swappable = "STAR_RATINGS_RATING_MODEL"


class UserRatingManager(models.Manager):
    def for_instance_by_user(self, instance, user):
        ct = ContentType.objects.get_for_model(instance)
        return self.filter(
            rating__content_type=ct, rating__object_id=instance.pk, user=user
        ).first()


class UserRating(models.Model):
    """
    An individual rating of a user against a model.
    """

    created = models.DateTimeField(_("created"), auto_now_add=True)
    modified = models.DateTimeField(_("modified"), auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE
    )
    # Unused: the rater IP is no longer recorded. Kept to leave the schema unchanged.
    ip = models.GenericIPAddressField(blank=True, null=True)
    score = models.PositiveSmallIntegerField()
    rating = models.ForeignKey(
        get_star_ratings_rating_model_name(),
        related_name="user_ratings",
        on_delete=models.CASCADE,
    )

    objects = UserRatingManager()

    class Meta:
        unique_together = ["user", "rating"]

    def __str__(self):
        return "{} rating {} for {}".format(
            self.user, self.score, self.rating.content_object
        )
