from django.urls import path

from . import views

app_name = "shop"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:product_id>/", views.details, name="details"),
    path("<int:product_id>/like", views.like, name="like"),
    path("<int:product_id>/add_to_cart", views.add_to_cart,
         name="add_to_cart"),
    path("<int:product_id>/buy/", views.purchase, name="purchase"),
]
