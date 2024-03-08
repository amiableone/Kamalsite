from django.db import models


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

    # TODO:
    #   1. Make save() interrupt if min_order is not specified
    #   and update min_order_amount each time min_order_quantity
    #   is updated.
    #   2. Create as many dummy methods for all models as needed
    #   for writing tests. Let's make the development of this
    #   project test-driven ;)

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


class User(models.Model):
    """This model will be replaced with the User model
    provided by Django. This one is for fooling around.
    """
    signed_up = models.BooleanField(default=False)

    # These fields may not accept null values if signed_up=True.
    name = models.CharField(max_length=20, null=True)
    user_email = models.EmailField(null=True)

    def __str__(self):
        if self.signed_up:
            return f"Name={self.name}"
        return f"Client not logged-in"


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
        return f"Made by {self.user}"


class OrderDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity_ordered = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Details of {self.order}"


class Comment(models.Model):
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry = models.TextField()

    def _shorten(self):
        extract = self.entry[:10] + "..."
        if len(extract) < len(self.entry):
            return extract
        return self.entry

    def __str__(self):
        return f"{self._shorten()}"
