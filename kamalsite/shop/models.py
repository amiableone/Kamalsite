import datetime

from django.db import models
from myauth.models import User


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
    sku = models.PositiveBigIntegerField(unique=True)
    colour = models.CharField(max_length=30)
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
            return # Can't save without specifying min_order

        super().save(*args, **kwargs)

    def in_stock(self):
        return self.quantity > 0

    def min_order_amount(self):
        return self.min_order_quantity * self.price

    def __str__(self):
        return f"{self.name.title()}"


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
    liked = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} liked {self.product}"


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
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
        return f"Owned by {self.user}"


class Addition(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    date_added = models.DateField(auto_now=True)

    # When Addition instance is created, it should be provided
    # min_order_quantity of the product it relates to as default.
    quantity = models.DecimalField(max_digits=12,  decimal_places=2)

    # ready_to_order is for identifiyng products create an order with.
    ready_to_order = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product} added to {self.cart}"


class Order(models.Model):
    # Clients should be able to create orders from Cart
    # as well as directly from a Product page.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="OrderDetail")

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
        # return f"Made by User"
        return f"Made by {self.user}"


class OrderDetail(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
    )
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

    payment_date = models.DateTimeField(auto_now_add=True)
    payment_received = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)


class Shipment(models.Model):
    """Shipment address to ship goods to. Can be created only for
    authenticated users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipment_address = models.CharField(max_length=300)


class Defect(models.Model):
    """Model for writing-off bad Products."""
    description = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=12)
