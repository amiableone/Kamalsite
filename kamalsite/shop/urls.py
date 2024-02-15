from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:product_id>/", views.details, name="details"),
    path("<int:product_id>/buy/", views.purchase, name="purchase"),
]
