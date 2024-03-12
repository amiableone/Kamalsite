from django.contrib import admin

from .models import User

class MyAdminSite(admin.AdminSite):
    site_title = "Power place"
    site_header = "МЕСТО СИЛЫ"
    index_title = "Админка Камалсайта"


admin_site = MyAdminSite(name="my_auth_admin")

admin_site.register(User)
