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

from .forms import (
    CatalogFilterForm,
    CatalogSortForm,
    LikeForm,
)
from .models import (
    Product,
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
    filter_settings = {}
    sort_settings = {}

    def get(self, request, *args, **kwargs):
        like_form = LikeForm
        like_forms = []
        for product in self.queryset:
            like_forms.append(
                like_form(
                    initial={"user": request.user.id, "product": product.id},
                )
            )
        # Other things like addition_form will be put in self.product_cards later.
        self.product_cards = zip(self.queryset, like_forms)
        request.session["page"] = kwargs["page"]
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ProductCardLikeView.as_view()
        return view(request, *args, **kwargs)

    post.alters_data = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = CatalogFilterForm()
        context["sort_form"] = CatalogSortForm()
        context["apply_button"] = _("Apply")
        context["like_button"] = _("Like")
        return context


class ProductCardLikeView(View):
    form_class = LikeForm
    initial = {}
    template_name = "shop/catalog.html"

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        try:
            like = Like.objects.get(
                user=request.user,
                product=kwargs["product_id"],
            )
        except Like.DoesNotExist:
            product = get_object_or_404(Product, id=kwargs["product_id"])
            like = Like(user=request.user, product=product)
            like.save()
        except KeyError:
            return Http404("Product does not exist.")
        form = self.form_class(request.POST, instance=like)
        page = request.session.get("page", 1)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(
            reverse("shop:catalog", kwargs={"page": page})
        )


class ProductDetailView(DetailView):
    """
    Display a product page.
    """
    context_object_name = "product"
    queryset = Product.objects.filter(in_production=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["like"] = _("Like")
        context["add_to_cart_button"] = _("Add to cart")
        context["buy_now_button"] = _("Buy now")
        return context
