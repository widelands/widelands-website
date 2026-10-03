import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import View

from . import get_star_ratings_rating_model
from .forms import RateForm


class Rate(LoginRequiredMixin, View):
    def get_object(self):
        """
        Returns the model instance we're rating from the URL params.
        """
        content_type = ContentType.objects.get_for_id(self.kwargs["content_type_id"])
        return content_type.get_object_for_this_type(pk=self.kwargs["object_id"])

    def post(self, request, *args, **kwargs):
        data = request.POST or json.loads(request.body.decode())

        return_url = data.get("next", "/")
        if not isinstance(return_url, str) or not url_has_allowed_host_and_scheme(
            return_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return_url = "/"

        form = RateForm(data)
        if form.is_valid():
            score = form.cleaned_data["score"]
            rating = get_star_ratings_rating_model().objects.rate(
                self.get_object(), score, user=request.user
            )
            result = rating.to_dict()
            result["user_rating"] = score
            res_status = 200
        else:
            result = {"errors": form.errors}
            res_status = 400

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(data=result, status=res_status)
        return HttpResponseRedirect(return_url)
