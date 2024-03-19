import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from shop.models import Product

# TODO:
#   -   I think it might be useful to track production status
#       and schedule of a product for several reasons.
#       1.  A product taken out of production (discontinued)
#           that is still in stock may be shown to a site user
#           in a special pop-up window that tells them that
#           they must hurry to buy it because it's almost gone.
#       2.  On the other hand, a product that is not in stock
#           and that was discontinued, automatically stops
#           being presented in the catalog.
#       3.  Production start date from the Production model
#           (that doesn't exist at the moment) might be used to
#           indicate new products for the NEW Category (that
#           also doesn't exist at the moment). It probably will
#           have to be the very first production start date in
#           case there are more than one (e.g. when production
#           is discontinued and then continued again).
#   -   Create model Collection to group Products by style
#       or production season. This might be an abstract
#       base model for Style and Season models. Products
#       from the same collection will not have to be under
#       the same category.
#   -   Maybe it makes sense to create models Facility and
#       Supplier.


class Component(models.Model):
    """Components and materials needed to produce a Product.
    `products` specifies products a component is used in production of.
    """
    name = models.CharField(max_length=50)
    unit_measure = models.CharField(max_length=50)
    products = models.ManyToManyField(Product)


class Supplies(models.Model):
    component = models.ForeignKey(
        Component,
        on_delete=models.SET_NULL,
        null=True,
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    class SOURCES(models.TextChoices):
        PRODUCED = "Produced", _("Produced")
        PURCHASED = "Purchased", _("Purchased")
        FOUND = "Found", _("Found")

    source = models.CharField(choices=SOURCES)
    supplier = models.ForeignKey(
        "Supplier",
        on_delete=models.SET_NULL,
        related_name="supplies",
        null=True,
    )
    order_date = models.DateTimeField(default=timezone.now)
    delivery = models.DateTimeField(null=True)
    actual_delivery = models.DateTimeField(null=True)
    cancelled = models.BooleanField(default=False)


class Supplier(models.Model):
    """Suppliers of components and materials.
    `components` specify what components may be ordered from the supplier.
    """
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, null=True)
    phone = models.BigIntegerField(null=True)
    address = models.CharField(max_length=200)
    owned = models.BooleanField(default=False)

    components = models.ManyToManyField(Component)


def production_complete_date():
    return datetime.date.today() + datetime.timedelta(days=14)

class Production(models.Model):
    """Each Production instance reflects a single process of converting
    some components from Supplies into a set of Products.
    """
    products = models.ManyToManyField(Product, through="ProductsMade")
    materials = models.ManyToManyField(Supplies, through="MaterialsUsed")
    start = models.DateField(default=datetime.date.today)
    end = models.DateField(default=production_complete_date)


class ProductsMade(models.Model):
    """Planned and actual quantities of a product as an outcome of a
    production process and its completeness status.
    """
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    plan_qty = models.DecimalField(max_digits=12, decimal_places=2)
    actual_qty = models.DecimalField(max_digits=12, decimal_places=2)
    complete = models.BooleanField(default=False)


class MaterialsUsed(models.Model):
    """How much of a certain supply was used in a certain process."""
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    supply = models.ForeignKey(Supplies, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
