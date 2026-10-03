import uuid
from decimal import Decimal

from django import template
from django.template import loader
from django.templatetags.static import static

from .. import app_settings, get_star_ratings_rating_model
from ..models import UserRating

register = template.Library()


@register.simple_tag(takes_context=True)
def ratings(
    context,
    item,
    icon_height=app_settings.STAR_RATINGS_STAR_HEIGHT,
    icon_width=app_settings.STAR_RATINGS_STAR_WIDTH,
    read_only=False,
    template_name="star_ratings/widget_base.html",
):
    request = context["request"]
    rating = get_star_ratings_rating_model().objects.for_instance(item)

    if request.user.is_authenticated:
        user_rating = UserRating.objects.for_instance_by_user(item, user=request.user)
    else:
        user_rating = None

    if user_rating is not None:
        user_rating_percentage = 100 * (
            user_rating.score / Decimal(app_settings.STAR_RATINGS_RANGE)
        )
    else:
        user_rating_percentage = None

    stars = [i for i in range(1, app_settings.STAR_RATINGS_RANGE + 1)]

    # We get the template to load here rather than using inclusion_tag so that the
    # template name can be passed as a template parameter
    return loader.get_template(template_name).render(
        {
            "rating": rating,
            "request": request,
            "user": request.user,
            "user_rating": user_rating,
            "user_rating_percentage": user_rating_percentage,
            "stars": stars,
            "star_count": app_settings.STAR_RATINGS_RANGE,
            "percentage": 100
            * (rating.average / Decimal(app_settings.STAR_RATINGS_RANGE)),
            "icon_height": icon_height,
            "icon_width": icon_width,
            "sprite_width": icon_width * 3,
            "sprite_image": static("star-ratings/images/stars.png"),
            "id": "dsr{}".format(uuid.uuid4().hex),
            "read_only": read_only,
            "editable": not read_only and request.user.is_authenticated,
        },
        request=request,
    )
