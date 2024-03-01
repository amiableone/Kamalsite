from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    in_stock = models.BooleanField(default=False)
    quantity = models.DecimalField("available quantity", default=0)
    quantity_measure = models.CharField(max_length=10)
    price_per_unit = models.DecimalField(decimal_places=2)

    class CurrencyChoice(models.TextChoices):
        RUB = "руб."
        USD = "долл."
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoice,
        default=CurrencyChoice.RUB,
    )

    # Specify at least one min_order parameter.
    # `min_order_quantity` is in natural terms and
    # `min_order_amount` is in monetary terms.
    min_order_quantity = models.DecimalField(null=True)
    min_order_amount = models.DecimalField(null=True)

    def __str__(self):
        return f"<Product {self.name.title()}>"


class User(models.Model):
    signed_up = models.BooleanField(default=False)

    # These field may not accept null values if signed_up=True.
    name = models.CharField(max_length=20, null=True)
    user_email = models.EmailField(null=True)
    user_type = models.CharField(choices=[])

    def __str__(self):
        if self.signed_up:
            return f"<User{self.pk} {self.name}>"
        return f"<Visitor>"


class Like(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"<Like: {self.product} liked by {self.user}>"


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    subcategory = models.ForeignKey(Category, on_delete=models.CASCADE)

    products = models.ManyToManyField(Product)

    def __str__(self):
        return f"<Category {self.name}>"


class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    products = models.ManyToManyField(Product, through=Addition)
    # TODO:
    #   Add a feature allowing purchasing products from the cart
    #   in separate orders.

    def __str__(self):
        return f"<Cart of {self.user}>"


class Addition(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateField()
    quantity_added = models.DecimalField()

    def __str__(self):
        return f"<Addition of {self.product} to {self.cart}>"


class Order(models.Model):
    # This should be possible to create from Cart
    # as well as directly from a Product page.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through=OrderDetail)

    def __str__(self):
        return f"<Order by {self.user}>"


class OrderDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    # Creating an order means confirming readiness to buy and pay.
    date_created = models.DateTimeField()
    quantity_ordered = models.DecimalField()
    date_paid = models.DateTimeField(null=True)


    def __str__(self):
        return f"<OrderDetail for {self.order}>"


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
        return f"<Comment by {self.user}: {self._shorten()}>"

# TODO:
#   Add models Page, Search, and similar for managing the site structure.
