from django.db import models
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
    """Components and materials needed to produce a Product."""
    products = models.ManyToManyField(Product)


class Facility(models.Model):
    """Production facilities owned."""
    products = models.ManyToManyField(Product)


class Supplier(models.Model):
    """Suppliers of components and materials."""
    components = models.ManyToManyField(Component)
