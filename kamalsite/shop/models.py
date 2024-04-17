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

    def amount(self):
        total = 0
        for a in self.addition_set.filter(order_now=True):
            total += a.product.price + a.quantity
        return total

    def __str__(self):
        return f"{self.user}'s cart"


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
        return f"{self.product} in {self.cart}"


class Order(models.Model):
    # TODO: Set on_delete to a callable returning deleted_user placeholder.
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    products = models.ManyToManyField(Product, through="OrderDetail")

    # Fill out purchaser and purchaser_email automatically with user data or
    # manually if user is null.
    # TODO:
    #   -   Customize fields for purchaser, purchaser_email, receiver, and
    #       receiver_email.
    # as_individual=True if user.organization is not None.
    as_individual = models.BooleanField(default=False)
    # purchaser is user.organization if as_individual=False.
    purchaser = models.CharField(max_length=50)
    purchaser_email = models.EmailField()
    receiver = models.CharField(max_length=50)
    receiver_phone = models.CharField(max_length=50)

    # A user can add shipment details beforehand and choose one of them when
    # filling out order details or create and save one right in the process.
    shipped = models.BooleanField(default=False)
    shipment = models.ForeignKey(
        "Shipment",
        on_delete=models.SET_NULL,
        null=True,
    )
    # shipment_company = models.ForeignKey(
    #     "ShipmentCompany",
    #     on_delete=models.SET_NULL,
    #     null=True,
    # )
    shipment_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    # Validate that confirmed=True only when purchaser/receiver data are filled.
    confirmed = models.BooleanField(default=False)

    # TODO:
    #   -   Make Order.quantity uneditable as soon as confirmed is set to
    #       True.
    #   -   Add `edit()` method to allow users to make requests to change
    #       quantities after confirming the order with a disclaimer that
    #       no guarantees that the request will be granted are implied.

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
            if self.user:
                return f"{self.user} ordered {products}"
            return f"Anonym ordered {products}"
        else:
            return "Unsaved order"


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
            )
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
    Shipment address to ship goods to. Can be created only for
    authenticated users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # TODO: Customize shipment_address field.
    shipment_address = models.CharField(max_length=300)
