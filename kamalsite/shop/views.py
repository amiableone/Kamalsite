from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from .models import Product

def index(request):
    most_popular_products = Product.objects.order_by("-likes")[:16]
    template = loader.get_template("shop/index.html")
    context = {
        "most_popular_products": most_popular_products,
    }
    return  HttpResponse(template.render(context, request))

def details(
        request,
        product_id,
):
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

def like(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.likes += 1
    product.save()
    return HttpResponseRedirect(
        reverse("shop:details", args=(product_id,))
    )

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.additions += 1
    product.save()
    return HttpResponseRedirect(
        reverse("shop:details", args=(product_id,))
    )
