from django.db import models
from myauth.models import User

# TODO:
#   -   Create as many dummy methods for all models as needed
#       for writing tests. Let's make the development of this
#       project test-driven ;)
#   -   Every time an order is created, Product.quantity is
#       adjusted accordingly. Adding a product to cart doesn't
#       change this parameter.
#   -   Every time an order is paid (Order instance paid
#       attribute becomes True), this should happen:
#       -   Purchase model (which currently doesn't exist)
#           is updated with a new entry,
#       -
#   -   Create Discount model with relations to Category,
#       Product, and production.Collection to make it easy to
#       add discounts in bulk.
#   -   Track popularity of products based on number of vists
#       of product pages, likes, number of purchases and
#       purchasers, and purchase amounts.
#   -   Add new fields, attributes, or methods to Product:
#       -   in_production BooleanField denoting that a product
#           is either can be produced or can be purchased from
#           suppliers.
#       -   stock_keeping_unit (or sku) field which will be
#           its identifier along with its id.
#       -   preorder BooleanField denoting that a product may
#           be purchased even though it's not currently in
#           production (in_production=False).
#   -   Price, popularity, novelty, and the SKU will be used
#       as parameters for users to sort products by on the
#       site.
#   -   Add new parameters to Order and/or Purchase:
#       -   time_before_ready() returning how long a client
#           will have to wait until either they can take what
#           they purchased or the goods can be sent to them.
#           This may be based on two things:
#           -   How much of this product can be produced in
#               one go (to be specified in ProductionDetails
#               for each product),
#           -   How much a client has ordered

class Product(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    price = models.DecimalField(
        null=True,
        max_digits=2,
        decimal_places=2,
    )
    unit_measure = models.CharField(
        max_length=10,
        default="units",
    )
    quantity = models.DecimalField(
        "available quantity",
        default=0,
        max_digits=10,
        decimal_places=2,
    )

    # Specify at least one min_order parameter.
    # `quantity` in units and `amount` in monetary terms.
    min_order_quantity = models.DecimalField(
        null=True,
        max_digits=5,
        decimal_places=2,
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
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="subcategories",
    )

    products = models.ManyToManyField(Product)

    def __str__(self):
        return f"{self.name}"


class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    products = models.ManyToManyField(Product, through="Addition")
    # TODO:
    #   Add a feature allowing purchasing products from the cart
    #   in separate orders.

    def __str__(self):
        return f"Owned by {self.user}"


class Addition(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    date_added = models.DateField()
    quantity_added = models.DecimalField(max_digits=5, decimal_places=2)
    ready_to_order = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product} added to {self.cart}"


class Order(models.Model):
    # Clients should be able to create orders from Cart
    # as well as directly from a Product page.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="OrderDetail")

    date_created = models.DateTimeField()
    paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField()

    def __str__(self):
        # return f"Made by User"
        return f"Made by {self.user}"


class OrderDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity_ordered = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Details of {self.order}"
