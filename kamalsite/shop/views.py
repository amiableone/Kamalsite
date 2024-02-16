from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader

from .models import Product

def index(request):
    most_popular_products = Product.objects.order_by("-likes")[:16]
    template = loader.get_template("shop/index.html")
    context = {
        "most_popular_products": most_popular_products,
    }
    return  HttpResponse(template.render(context, request))

def details(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    context = {
        "product": product,
    }
    return render(request, "shop/details.html", context)

def purchase(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    context = {
        "product": product,
    }
    return render(request, "shop/buy.html", context)
