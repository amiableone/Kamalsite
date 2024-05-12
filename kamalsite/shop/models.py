import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import ObjectDoesNotExist

# TODO:
#   -   Track popularity of products based on number of visits of product
#       pages, likes, number of purchases and purchasers, and purchase
#       amounts.

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="deleted")[0]


class Product(models.Model):
    name = models.CharField(max_length=75)
    description = models.TextField()

    price = models.DecimalField(max_digits=12, decimal_places=2)
    unit_measure = models.CharField(max_length=30, default="units")
    quantity = models.DecimalField(
        "available quantity",
        default=0,
        max_digits=12,
        decimal_places=2,
    )
    min_order_quantity = models.DecimalField(max_digits=12, decimal_places=2)

    # Use date_created to sort by novelty and in_production
    # to control visibility of products in the catalog.
    date_created = models.DateField(
        default=datetime.date.today,
        help_text="when first appeared in the catalog",
    )
    in_production = models.BooleanField(default=True)
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


class TrueLikesQuerySet(models.QuerySet):
    def qty(self):
        return self.filter(liked=True).count()


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET(get_sentinel_user),
        related_name="likes",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    liked = models.BooleanField(default=False)

    objects = TrueLikesQuerySet.as_manager()

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
    name = models.CharField(
        max_length=50,
        help_text="e.g. size, colour, furniture type, etc.",
    )
    value = models.CharField(max_length=50)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="subcategories",
        null=True,
    )
    products = models.ManyToManyField(Product)

    class Meta:
        ordering = ["name", "value"]

    def __str__(self):
        return f"{self.name} {self.value}"


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

    category = models.ManyToManyField(Category)

    def within_range(self):
        return 0 <= self.percent <= 70


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET(get_sentinel_user),
    )
    products = models.ManyToManyField(Product, through="Addition")

    def amount(self):
        total = 0
        for a in self.addition_set.filter(order_now=True):
            total += a.product.price * a.quantity
        return total

    def __str__(self):
        if self.pk:
            products = [p.name for p in self.products.all()]
            return f"{products}"
        else:
            return "incomplete"


class Addition(models.Model):
    """
    A model connecting a certain product to a certain cart.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    # quantity is set to related product min_order_quantity when created
    # from a corresponding form.
    quantity = models.DecimalField(max_digits=12,  decimal_places=2)

    # order_now is for specifying which products in cart to order.
    order_now = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "cart"],
                name="unique_product_cart",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.quantity:
            self.order_now = False
        super().save(*args, **kwargs)

    def __str__(self):
        try:
            return f"{self.product} in cart #{self.cart_id}"
        except ObjectDoesNotExist:
            return "incomplete"


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET(get_sentinel_user),
        related_name="orders",
    )
    products = models.ManyToManyField(Product, through="OrderDetail")
    date_created = models.DateTimeField(auto_now_add=True)

    # TODO:
    #   -   Customize fields for purchaser, purchaser_email, receiver, and
    #       receiver_email.
    as_individual = models.BooleanField(default=False)
    # purchaser is user.organization if as_individual=False.
    purchaser = models.CharField(max_length=50)
    purchaser_email = models.EmailField()
    receiver = models.CharField(max_length=50)
    receiver_phone = models.CharField(max_length=50)

    # A user can add shipment details beforehand and choose one of them when
    # filling out order details or create and save one right in the process.
    shipped = models.BooleanField(default=False)
    shipment = models.ForeignKey("Shipment", null=True, on_delete=models.SET_NULL)
    # Validate that confirmed=True only when purchaser/receiver data are filled.
    confirmed = models.BooleanField(default=False)

    # TODO:
    #   -   Make Order.quantity uneditable as soon as confirmed=True.

    def quantity(self):
        """
        Return quantity of each product.
        """
        return [(d.product, d.quantity) for d in self.order_details.all()]

    def amount(self):
        """
        Return total monetary amount of the order.
        """
        total = 0
        for detail in self.order_details.all():
            total += detail.product.price * detail.quantity
        return total

    def make_purchase(self):
        if self.confirmed and not hasattr(self, "purchase"):
            p = Purchase(order=self)
            p.save()

    def completed(self):
        try:
            return self.purchase.payment_received
        except Purchase.DoesNotExist:
            return False

    def __str__(self):
        if self.pk:
            products = [p.name for p in self.products.all()]
            return f"{products}"
        else:
            return "incomplete"


class OrderDetail(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_details",
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "order"],
                name="unique_product_order",
            ),
        ]
    # Don't override save() as bulk_create is called when an Order instance
    # is created.

    def __str__(self):
        return f"for {self.product} in Order#{self.order.pk}"


class Purchase(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    date_created = models.DateTimeField(auto_now_add=True)
    payment_received = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)


class Shipment(models.Model):
    """
    Shipment address to ship goods to.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET(get_sentinel_user),
    )
    address = models.CharField(max_length=300)
    zip = models.CharField(max_length=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "address"],
                name="unique_user_address",
            ),
        ]

    def __str__(self):
        try:
            city = self.address.split(", ")[2]
            return f"to {city}"
        except ValueError:
            return "unsaved"
