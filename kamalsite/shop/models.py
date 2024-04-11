import datetime

from django.db import models
from myauth.models import User


# TODO:
#   -   Create as many dummy methods for all models as needed for writing
#       tests. Let's make the development of this project test-driven ;)
#   -   Track popularity of products based on number of vists of product
#       pages, likes, number of purchases and purchasers, and purchase
#       amounts.
#   -   Price, popularity, and novelty will be used as parameters
#       for users to sort products by on the site.
#       -   Hence, add an on_sale_since field to Product.

class Product(models.Model):
    name = models.CharField(max_length=75)
    description = models.TextField()
    sku = models.PositiveBigIntegerField(unique=True)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    unit_measure = models.CharField(max_length=30, default="units")
    quantity = models.DecimalField(
        "available quantity",
        default=0,
        max_digits=12,
        decimal_places=2,
    )
    min_order_quantity = models.DecimalField(max_digits=12, decimal_places=2)

    # Use date_created to sort by novelty and in_production to remove from the
    # catalog when quantity reaches zero.
    date_created = models.DateField(
        default=datetime.date.today,
        help_text="when first appeared in the catalog",
    )
    in_production = models.BooleanField(default=True)

    collection = models.ForeignKey(
        "Collection",
        on_delete=models.SET_NULL,
        null=True,
    )
    discount = models.ForeignKey(
        "Discount",
        on_delete=models.SET_NULL,
        null=True,
    )

    def save(self, *args, **kwargs):
        if self.min_order_quantity is None:
            return  # Can't save without specifying min_order

        super().save(*args, **kwargs)

    def in_stock(self):
        return self.quantity > 0

    def min_order_amount(self):
        return self.min_order_quantity * self.price

    def __str__(self):
        return f"{self.name}"


class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="likes",
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
        return f"user={self.user}, product={self.product}, liked={self.liked}"


class Category(models.Model):
    # TODO:
    #   -   It may make sense to create subclasses of this model for each
    #       category type. But then there would have to be a way of creating
    #       such subclasses from the admin site or else Erika wouldn't be able
    #       to create new types of categories.
    ctg_type = models.CharField(
        max_length=50,
        help_text="e.g. size, colour, furniture type, etc.",
    )
    name = models.CharField(max_length=50)
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="subcategories",
        null=True,
    )

    products = models.ManyToManyField(Product)

    def __str__(self):
        return f"{self.name}"


class Collection(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    date_created = models.DateField(default=datetime.date.today)

    # Allow users to see this collection.
    visible = models.BooleanField(default=False)

    discount = models.ForeignKey(
        "Discount",
        on_delete=models.SET_NULL,
        null=True,
    )


def discount_end_date():
    """Return a date two weeks from now."""
    return datetime.date.today() + datetime.timedelta(days=14)

class Discount(models.Model):
    reason = models.CharField(max_length=50)
    # TODO:
    #   -   Replace with a custom field that corresponds to percentage values
    #       in postgresql.
    percent = models.PositiveSmallIntegerField()
    seasonal = models.BooleanField(default=False)
    start = models.DateField(default=datetime.date.today)
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
        return f"owner={self.user}"


class Addition(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    # When Addition instance is created, it should be provided
    # min_order_quantity of the product it relates to as default.
    quantity = models.DecimalField(max_digits=12,  decimal_places=2)

    # ready_to_order is for checking products to put in a confirmed order.
    ready_to_order = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product} in {self.cart}"


class Order(models.Model):
    # Clients should be able to create orders from Cart
    # as well as directly from a Product page.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="OrderDetail")

    receiver = models.CharField(max_length=50)
    # TODO:
    #   -   Add receiver_phone field.

    # A user can add shipment details beforehand and choose one of them
    # when filling out order details.
    # Or they can add shipment details right when filling out order
    # details, in which case they can save these details which will attach
    # them to their profile by creating a Shipment instance based on the
    # shipment_address value.
    shipped = models.BooleanField(default=False)
    shipment_address = models.CharField(max_length=300)
    shipment_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)

    # TODO:
    #   -   Make Order.quantity uneditable as soon as confirmed is set to
    #       True.
    #   -   Add `edit()` method to allow users to make requests to change
    #       quantities after confirming the order with a disclaimer that
    #       no guarantees that the request will be granted are implied.

    def amount(self):
        """Compute total amount of the order and return a tuple of the
        order price and the cost of shipment.
        """
        total = 0
        for detail in self.orderdetail_set:
            element = detail.product.price * detail.quantity_ordered
            total += element
        return total, self.shipment_cost

    def make_purchase(self):
        if self.confirmed and not hasattr(self, "purchase"):
            p = Purchase(order=self)
            p.save()

    def completed(self):
        try:
            return self.purchase.payment_received
        except Purchase.DoesNotExist:
            return False

    def save(self, *args, **kwargs):
        for detail in self.orderdetail_set:
            if detail.quantity < detail.product.min_order_quantity:
                return

        super().save(*args, **kwargs)

    def __str__(self):
        return f"creator={self.user}"


class OrderDetail(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"for {self.order}"


class Purchase(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    payment_date = models.DateTimeField(auto_now_add=True)
    payment_received = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)


class Shipment(models.Model):
    """
    Shipment address to ship goods to. Can be created only for
    authenticated users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipment_address = models.CharField(max_length=300)
