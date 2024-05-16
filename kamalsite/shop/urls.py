from django.urls import path
from django.views.generic.base import RedirectView

from . import views

app_name = "shop"
urlpatterns = [
    # redirect shop to catalog with page=1:
    path("", views.NoPageRedirectView.as_view(), name="shop"),
    path("page<int:page>/", views.CatalogView.as_view(), name="catalog"),
    path("filtered/", views.CatalogFilterView.as_view(), name="catalog-filter"),
    path(
        "like-<int:product_id>/",
        views.ProductCardLikeView.as_view(),
        name="product-card-like",
    ),
    path(
        "add-<int:product_id>/",
        views.ProductCardAdditionView.as_view(),
        name="product-card-add",
    ),
    path("product<int:pk>/", views.ProductDetailView.as_view(), name="product-detail"),
]
