from django.urls import path
from django.views.generic.base import RedirectView

from .views import NoPageRedirectView, CatalogView, ProductDetailView

app_name = "shop"
urlpatterns = [
    # redirect shop to catalog with page=1:
    path("", NoPageRedirectView.as_view(), name="shop"),
    path("page<int:page>/", CatalogView.as_view(), name="catalog"),
    path("product<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
]
