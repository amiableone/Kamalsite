from django.contrib import admin

from .models import Product


class MyAdminSite(admin.AdminSite):
    site_title = "Power place"
    site_header = "МЕСТО СИЛЫ"
    index_title = "Админка Камалсайта"


admin_site = MyAdminSite(name="kamaladmin")

admin_site.register(Product)
