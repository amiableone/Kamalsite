from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import (
    HttpResponse,
    Http404,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.base import RedirectView

from . import forms
from . import models


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
    queryset = models.Product.objects.filter(in_production=True)
    template_name = "shop/catalog.html"
    like_form = forms.LikeForm
    add_form = forms.CreateAdditionForm
    filter_form = forms.CatalogFilterForm
    sort_form = forms.CatalogSortForm

    def get(self, request, *args, **kwargs):
        like_forms = []
        add_forms = []
        addition_ = models.Addition

        qs = self.get_queryset()
        for product in qs:
            like_forms.append(self.like_form())
            if addition_.objects.filter(
                cart=request.user.cart,
                product=product,
            ).exists():
                add_forms.append(True)
            else:
                add_forms.append(
                    self.add_form(initial={"product": product.id})
                )
        self.product_cards = zip(qs, like_forms, add_forms)
        request.session["page"] = kwargs["page"]
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        views = {
            "like": ProductCardLikeView.as_view,
            "addition": ProductCardAdditionView.as_view,
        }
        action = request.POST.get("action")
        view = views.get(action, NoPageRedirectView.as_view)()
        return view(request, *args, **kwargs)

    post.alters_data = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form()
        context["sort_form"] = self.sort_form()
        context["apply_button"] = _("Apply")
        context["like_button"] = _("Like")
        context["add_to_cart_button"] = _("Add to cart")
        context["link_to_cart"] = _("To cart")
        return context

    def get_queryset(self):
        self.update_filter_settings()
        self.filter_queryset()
        return self.queryset

    def update_filter_settings(self):
        if self.request.GET.get("action") == "filter_catalog":
            self.request.session["filter_settings"] = self.request.GET

    def filter_queryset(self):
        try:
            filters = self.request.session["filter_settings"]
            limit_to = Q(
                price__gte=filters["price_range"][0],
                price__lte=filters["price_range"][1],
            )
            types = filters["types"]
            for t in types:
                limit_to |= Q(category__in=filters[t])
            # TODO: exclude unmarked child categories of which parent categories
            #   were chosen.
            if filters["retail"]:
                limit_to |= Q(quantity__gt=0) | Q(min_order_quantity=0)
            self.queryset = self.queryset.filter(limit_to)
        except KeyError:
            pass

    def get_ordering(self):
        self.update_sort_settings()
        try:
            params = self.request.session["sort_settings"]
            sort_by = params["sort_by"][0]
            ascending = params["ascending"]
            # TODO: Work on what to sort on when popularity is chosen.
            cases = {
                "name": "name",
                "popularity": "likes",
                "price": "price",
                "novelty": "date_created"
            }
            if ascending:
                self.ordering = cases.get(sort_by, self.ordering)
            else:
                self.ordering = "-" + cases.get(sort_by, self.ordering)
        except KeyError:
            pass
        return self.ordering

    def update_sort_settings(self):
        if self.request.GET.get("action") == "sort_catalog":
            self.request.session["sort_settings"] = self.request.GET


class ProductCardLikeView(View):
    form_class = forms.LikeForm
    template_name = "shop/catalog.html"

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        like_ = models.Like
        product_ = models.Product
        try:
            like = like_.objects.get(
                user=request.user,
                product=kwargs["product_id"],
            )
        except like_.DoesNotExist:
            product = get_object_or_404(product_, id=kwargs["product_id"])
            like = like_(user=request.user, product=product)
            like.save()
        except KeyError:
            return Http404("Product does not exist.")
        form = self.form_class(request.POST, instance=like)
        if form.is_valid():
            form.save()
        page = request.session.get("page", 1)
        return HttpResponseRedirect(
            reverse("shop:catalog", kwargs={"page": page})
        )


class ProductCardAdditionView(View):
    form_class = forms.CreateAdditionForm
    template_name = "shop/catalog.html"

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        addition_ = models.Addition
        product_ = models.Product
        try:
            try:
                cart = request.user.cart
            except models.Cart.DoesNotExist:
                cart = models.Cart(user=request.user)
            addition = addition_.objects.get(
                cart=cart,
                product=kwargs["product_id"],
            )
        except addition_.DoesNotExist:
            product = get_object_or_404(product_, id=kwargs["product_id"])
            addition = addition_(cart=cart, product=product)
        except KeyError:
            return Http404("Product does not exist.")
        form = self.form_class(request.POST, instance=addition)
        if form.is_valid():
            form.save()
        page = request.session.get("page", 1)
        return HttpResponseRedirect(
            reverse("shop:catalog", kwargs={"page": page})
        )


class ProductDetailView(DetailView):
    """
    Display a product page.
    """
    context_object_name = "product"
    queryset = models.Product.objects.filter(in_production=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["like"] = _("Like")
        context["add_to_cart_button"] = _("Add to cart")
        context["buy_now_button"] = _("Buy now")
        return context
