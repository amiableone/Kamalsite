from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.base import RedirectView

from .forms import (
    CatalogFilterForm,
    CatalogSortForm,
    LikeForm,
)
from .models import (
    Product,
    User,
    Like,
)


class NoPageRedirectView(RedirectView):
    pattern_name = "shop:catalog"

    def get_redirect_url(self, *args, **kwargs):
        kwargs["page"] = 1
        return super().get_redirect_url(*args, **kwargs)


class CatalogView(ListView):
    """
    Display products.
    """
    context_object_name = "catalog"
    ordering = "-likes"
    paginate_by = 4
    queryset = Product.objects.filter(in_production=True)
    template_name = "shop/catalog.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = CatalogFilterForm
        context["sort_form"] = CatalogSortForm
        context["like_form"] = LikeForm
        context["apply"] = _("Apply")
        context["like"] = _("Like")
        return context


class ProductDetailView(DetailView):
    """
    Display a product page.
    """
    context_object_name = "product"
    queryset = Product.objects.filter(in_production=True)
