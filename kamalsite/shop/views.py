from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return  HttpResponse("This is the shop index.")

def details(request, product_id):
    return HttpResponse(f"This is the detail page for product {product_id}")

def purchase(request, product_id):
    return HttpResponse(f"This is the purchase page for product {product_id}")
