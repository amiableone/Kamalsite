from django.db import models
from myauth.models import User
from django.utils import timezone

from datetime import datetime, timedelta

# TODO:
#   -   Create as many dummy methods for all models as needed for writing
#       tests. Let's make the development of this project test-driven ;)
#   -   Every time an order is created, this should happen:
#       -   Product.quantity is adjusted accordingly. (Adding a product to
#           cart doesn't change this parameter.)
#           -   TO BE PROGRAMMED IN VIEW
#       -   User is urged to fill out an order form (doesn't yet exists).
#   -   Every time an order is paid (Order instance paid attribute becomes
#       True), this should happen:
#       -   Purchase model (which currently doesn't exist) is updated with
#           a new entry with data from the order form filled out by the
#           user.
#       -
#   -   Create Discount model with relations to Category, Product, and
#       production.Collection to make it easy to add discounts in bulk.
#   -   Track popularity of products based on number of vists of product
#       pages, likes, number of purchases and purchasers, and purchase
#       amounts.
#   -   Add new fields, attributes, or methods to Product:
#       -   in_production BooleanField denoting that a product is either
#           can be produced or can be purchased from suppliers.
#       -   stock_keeping_unit (or sku) field which will be its identifier
#           along with its id.
#       -   preorder BooleanField denoting that a product may be purchased
#           even though it's not currently in production
#           (in_production=False).
#   -   Price, popularity, novelty, and the SKU will be used as parameters
#       for users to sort products by on the site.
#   -   Add new parameters to Order and/or Purchase:
#       -   time_before_ready() returning how long a client will have to
#           wait until either they can take what they purchased or the
#           goods can be sent to them. This may be based on two things:
#           -   How much of this product can be produced in one go (to be
#               specified in ProductionDetails for each product),
#           -   How much a client has ordered

class Product(models.Model):
    name = models.CharField(max_length=75)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    unit_measure = models.CharField(
        max_length=30,
        default="units",
    )
    quantity = models.DecimalField(
        "available quantity",
        default=0,
        max_digits=12,
        decimal_places=2,
    )

    # Specify at least one min_order parameter.
    # `quantity` in units and `amount` in monetary terms.
    min_order_quantity = models.DecimalField(
        null=True,
        max_digits=12,
        decimal_places=2,
    )

    collection = models.ForeignKey(
        "Collection",
        on_delete=models.CASCADE,
        null=True,
    )
    discount = models.ForeignKey(
        "Discount",
        on_delete=models.SET_NULL,
        null=True,
    )

    def save(self, *args, **kwargs):
        if self.min_order_quantity is None:
            return # Can't save without specifying min_order

        super().save(*args, **kwargs)

    def in_stock(self):
        return self.quantity > 0

    def min_order_amount(self):
        return self.min_order_quantity * self.price

    def __str__(self):
        return f"{self.name.title()}"


# Maybe Django provides something useful for the same purpose
# these commented out models below are for. I'll keep them
# commented out until they or their Django versions are necessary.
#
# class SiteVisit(models.Model):
#     """Track site visits."""
#     visit_date = models.DateTimeField()
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#
#
# class ProductVisit(SiteVisit):
#     """Track product page visits."""
#     # Where did a user come from to this product page
#     # (none means from outside):
#     from_main = models.BooleanField(default=False)
#     from_catalog = models.BooleanField(default=False)
#     from_similar = models.BooleanField(default=False)
#     # TODO:
#     #   If possible and reasonable, add a visit duration tracker.
#     #   I also could add something like an action tracker to log
#     #   actions such as likes, additions, commenting, studying
#     #   colours, adjusting quantities, going to similar products,
#     #   etc.
#
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="liked_products",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="liked_by",
    )
    liked = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product",
            ),
        ]

    def __str__(self):
        # return f"User liked {self.product}"
        return f"{self.user} liked {self.product}"


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="subcategories",
    )

    products = models.ManyToManyField(Product)

    def __str__(self):
        return f"{self.name}"


class Collection(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    date_created = models.DateTimeField(default=timezone.now)

    # Allow users to see this collection.
    visible = models.BooleanField(default=False)

    discount = models.ForeignKey(
        "Discount",
        on_delete=models.SET_NULL,
        null=True,
    )


def discount_end_date():
    """Return a date two weeks from now."""
    return timezone.now() + timedelta(days=14)

class Discount(models.Model):
    reason = models.CharField(max_length=50)
    percent = models.PositiveSmallIntegerField()
    seasonal = models.BooleanField(default=False)
    start = models.DateField(default=timezone.now)
    end = models.DateField(default=discount_end_date)

    # This is a user group name or an empty string.
    group = models.CharField(max_length=50)

    def within_range(self):
        return 0 <= self.percent <= 70


class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    products = models.ManyToManyField(Product, through="Addition")

    def __str__(self):
        return f"Owned by {self.user}"


class Addition(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    date_added = models.DateField(auto_now=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)

    # ready_to_order is for identifiyng products create an order with.
    ready_to_order = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product} added to {self.cart}"


class Order(models.Model):
    # Clients should be able to create orders from Cart
    # as well as directly from a Product page.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="OrderDetail")

    # Learn how to use tzinfo of datetime
    date_created = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def amount(self):
        total = 0
        for detail in self.orderdetail_set:
            part = detail.product.price * detail.quantity_ordered
            total += part
        return total

    def pay(self, shipment=None):
        if not self.paid and not hasattr(self, "purchase"):
            p = Purchase(
                order=self,
                # DateTimeField is filled automatically.
                shipment=shipment,
            )
            p.save()

    def save(self, *args, **kwargs):
        for detail in self.orderdetail_set:
            if detail.quantity < detail.product.min_order_quantity:
                return

        super().save(*args, **kwargs)

    def __str__(self):
        # return f"Made by User"
        return f"Made by {self.user}"


class OrderDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Details of {self.order}"


class Purchase(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    payment_date = models.DateTimeField(auto_now=True)

    # A user can add shipment details beforehand and choose one of them
    # when filling out order details.
    # Or they can add shipment details right when filling out order details,
    # in which case they will be asked if they want to save these details.
    shipment = models.ForeignKey("Shipment", on_delete=models.CASCADE)


class Shipment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipment_address = models.CharField(max_length=300)
