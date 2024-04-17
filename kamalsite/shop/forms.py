from django import forms
from django.contrib.postgres.forms.ranges import IntegerRangeField
from django.core.exceptions import ValidationError
from django.db.models import Min, Max, TextChoices
from django.utils.translation import gettext_lazy as _

from .models import (
    Addition,
    Category,
    Like,
    Order,
    OrderDetail,
    Product,
)

# TODO.
#   -   Create these forms:
#       -   For filtering products in the catalog - DONE,
#       -   For sorting products in the catalog - DONE,
#       -   For liking/disliking a product - DONE,
#           -   Use sessions to disallow repeated likes/dislikes, additions
#               (this will be done in views).
#       -   For adding a product to cart - DONE,
#       -   For changing the quantity of a product in cart - DONE,
#       -   For deleting products from cart - DONE,
#           -   All of these operations with products in cart should be
#               preferrably done in a way that allows for recalculation of
#               the total price displayed right in the template (without
#               overhead of additional post requests).
#       -   For creating orders (e.g. by clicking on 'Buy' in a cart),
#       -   For filling out order details,
#           -   (Specify details of what fields are required here),
#   -   Create a bug report for:
#       -   Product.objects.filter(price__contained_by=nr) - where nr is a
#           NumericRange instance - raises django.core.exceptions.FieldError:
#           Unsupported lookup 'contained_by' for DecimalField or join on the
#           field not permitted (even when nr is based on Decimal values).
#           The documentation says contained_by supports DecimalField.


class PriceRangeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = {
            "min_price": forms.NumberInput,
            "max_price": forms.NumberInput,
        }
        super().__init__(widgets=widgets, attrs=attrs)

    def decompress(self, value):
        if value:
            return [i for i in value]
        return [None, None]


class PriceRangeField(forms.MultiValueField):
    """
    A field for specifying price range of Product instances through
    CatalogFilterForm.
    """
    # There's the IntegerRangeField in django.contrib.postgres.forms.ranges
    # but I decided to create my own to feel it. My version compresses
    # the input to a simple tuple, not some fancy psycopg Range instance.
    # It's yet to see if it proves to be sufficient this way.

    def __init__(self, **kwargs):
        price_extremes = Product.objects.aggregate(
            min_price=Min("price"),
            max_price=Max("price"),
        )
        min_price = price_extremes["min_price"]
        max_price = price_extremes["max_price"]
        fields = (
            forms.IntegerField(
                initial=min_price,
                min_value=min_price,
                required=False,
            ),
            forms.IntegerField(
                initial=max_price,
                max_value=max_price,
                required=False,
            ),
        )
        super().__init__(
            fields=fields,
            require_all_fields=False,
            required=False,
            widget=PriceRangeWidget,
            **kwargs,
        )

    def compress(self, data_list):
        lo, hi = data_list
        if lo and hi and lo > hi:
            raise ValidationError(
                "Min price higher than Max price",
                code="min_gt_max",
            )
        return tuple(data_list)


class CatalogFilterForm(forms.Form):
    """
    A form for filtering products in the catalog.
    Each Category.ctg_type corresponds to a ModelMultipleChoiceField.
    """

    # Find out how to declare fields dynamically based on existing ctg_type
    # values. Using setattr in __init__ doesn't create the fields.
    colour = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(ctg_type="colour"),
        required=False,
        to_field_name="name",
        widget=forms.CheckboxSelectMultiple,
    )
    size = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(ctg_type="size"),
        required=False,
        to_field_name="name",
        widget=forms.CheckboxSelectMultiple,
    )
    price_range = PriceRangeField()

    # TODO.
    #   -   Add these fields:
    #       -   Customize ModelMultipleChoiceField or SelectMultiple to allow for
    #           a neutral choice in addition to including/excluding. An alternative
    #           would be to create a separate form for excluding categories,
    #       -   A field for choosing Collection instances,
    #   -   Selecting a category should make its subcategories selected,

    # template_name is a property returning the value of form_template_name
    # of the renderer. It may be overridden like this:
    # template_name = "catalog_filter_snippet.html"


class CatalogSortForm(forms.Form):
    """
    A form for sorting products in the catalog.
    """

    class SortBy(TextChoices):
        PRICE = "price", _("Price")
        POPULARITY = "popularity", _("Popularity")
        NOVELTY = "novelty", _("Novelty")

    sort_by = forms.ChoiceField(
        choices=SortBy,
        initial=SortBy.NOVELTY,
    )
    ascending = forms.BooleanField(
        initial=False,
        required=False,
    )


class LikeForm(forms.ModelForm):
    class Meta:
        model = Like
        fields = ["user", "product"]
        widgets = {
            "user": forms.HiddenInput,
            "product": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].disabled = True
        self.fields["product"].disabled = True


class AdditionForm(forms.ModelForm):
    class Meta:
        model = Addition
        fields = ["cart", "product"]
        widgets = {
            "cart": forms.HiddenInput,
            "product": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cart"].disabled = True
        self.fields["product"].disabled = True


class CreateAdditionForm(AdditionForm):
    """
    Add products to cart (and create Addition instances) with this form.
    """

    def save(self, commit=True):
        addition = super().save(commit=False)
        addition.quantity = addition.product.min_order_quantity
        if commit:
            addition.save()
        return addition


class AdditionQuantityForm(AdditionForm):
    """
    Change quantity of a product in cart (specified in Addition.quantity).
    Specify if a product is to be ordered (or kept in cart idly).
    Initiate with an Addition instance.
    """

    class Meta(AdditionForm.Meta):
        fields = AdditionForm.Meta.fields + ["quantity", "order_now"]

    def clean(self):
        super().clean()
        qty = self.cleaned_data["quantity"]
        product = self.instance.product
        available = product.quantity
        minimum = product.min_order_quantity
        params = {
            "available": available,
            "minimum": minimum,
            "units": product.unit_measure,
        }
        if available < qty < minimum:
            if available:
                message = _("Can't order less than %(minimum)s %(units)s and more "
                            "than %(available)s %(units)s of this product.")
            else:
                message = _("Can't order less than %(minimum)s %(units)s of this "
                            "product when available quantity is 0.")
            error = ValidationError(
                message,
                code="too_low",
                params=params,
            )
            self.add_error("quantity", error)
        elif qty <= 0:
            message = _("Quantity must be positive.")
            error = ValidationError(
                message,
                code="non_positive",
                params=params,
            )
            self.add_error("quantity", error)


class DeleteAdditionForm(AdditionForm):
    """
    Delete product from cart.
    """

    def save(self, commit=True):
        addition = super().save(commit=False)
        addition.quantity = 0
        addition.order_now = False
        if commit:
            addition.save()
        return addition


class CreateOrderForm(forms.ModelForm):
    """
    Essentially a buy button.
    """
    from_cart = forms.BooleanField(
        disabled=True,
        required=False,
        widget=forms.HiddenInput,
    )
    # Display quantity field as hidden if from_cart=True.
    quantity = forms.DecimalField(required=False)

    class Meta:
        model = Order
        fields = ["user"]
        widgets = {"user": forms.HiddenInput}

    def __init__(self, *args, product=None, **kwargs):
        if not kwargs["initial"]["from_cart"]:
            if not product:
                raise TypeError("product must be Product object when from_cart=False")
            self.product = product
        super().__init__(*args, **kwargs)
        if self.product:
            self.fields["quantity"].required = True
        self.fields["user"].disabled = True

    def clean(self):
        super().clean()
        from_cart = self.cleaned_data["from_cart"]
        if not from_cart and "quantity" in self.cleaned_data:
            minimum = self.product.min_order_quantity
            qty = self.cleaned_data["quantity"]
            if qty < minimum:
                error = ValidationError(
                    message=_("Quantity must be at least %(minimum)s %(units)s."),
                    code="too_low",
                    params={
                        "minimum": minimum,
                        "units": self.product.unit_measure,
                    }
                )
                self.add_error("quantity", error)

    def save(self, commit=True):
        order = super().save(commit=False)
        order.save()
        cart = order.user.cart.products.all()
        if self["from_cart"].value():
            order_now = Addition.objects.filter(product__in=cart, order_now=True)
            OrderDetail.objects.bulk_create(
                [
                    OrderDetail(
                        order=order,
                        product=a.product,
                        quantity=a.quantity,
                    ) for a in order_now
                ]
            )
        else:
            OrderDetail.objects.create(
                order=order,
                product=self.product,
                quantity=self.cleaned_data["quantity"],
            )
        return order


class FullNameWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = {
            "last": forms.TextInput,
            "first": forms.TextInput,
            "middle": forms.TextInput,
        }
        super().__init__(widgets=widgets, attrs=attrs)

    def decompress(self, value):
        if isinstance(value, str):
            name = value.split(" ")
            return  [i for i in name]
        return [None, None, None]


class FullNameField(forms.MultiValueField):
    """
    A field for specifying a person's full name.
    """

    # This field corresponds to a CharField with max_length specidfied.
    # Until that's replaced with a more appropriate field, this field's
    # __init__ will accept max_length.
    def __init__(self, max_length=None, **kwargs):
        fields = (
            forms.CharField(
                max_length=20,
                error_messages={"incomplete": "Enter the last name."},
            ),
            forms.CharField(
                max_length=20,
                error_messages={"incomplete": "Enter the first name."},
            ),
            forms.CharField(
                initial=_("Optional"),
                max_length=20,
                required=False,
            ),
        )
        super().__init__(
            fields=fields,
            require_all_fields=False,
            widget=FullNameWidget,
            **kwargs,
        )

    def compress(self, data_list):
        last, first, middle = data_list
        full_name = first, last, middle
        return " ".join([i for i in full_name if i])


class OrderForm(forms.ModelForm):
    """
    A form for filling out order parameters.
    """
    # Control hiddenness of receiver and receiver_phone fields.
    receiver_is_purchaser = forms.BooleanField(required=False)

    class Meta:
        model = Order
        fields = [
            "user",
            "purchaser",
            "purchaser_email",
            "receiver",
            "receiver_phone",
            "shipped",
            "shipment",
            # shipment_company field is to be included
        ]
        field_classes = {
            "purchaser": FullNameField,
        }
        widgets = {
            "user": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        if "instance" not in kwargs:
            raise TypeError("instance argument is required")
        order = kwargs["instance"]
        user = order.user
        if not user.is_anonymous:
            if user.organization:
                order.purchaser = user.organization
                order.receiver = user.get_full_name()
            else:
                order.purchaser = user.get_full_name()
            order.purchaser_email = user.email
        super().__init__(*args, **kwargs)
        self.fields["user"].disabled = True
        self.fields["shipment"].required = False
        # self.fields["shipment_company"].required = False

    def clean(self):
        super().clean()
        shipped = self.cleaned_data["shipped"]
        shipment = self.cleaned_data["shipment"]
        if shipped and not shipment:
            error = ValidationError(
                message=_("Shipment address is not specified."),
                code="empty_shipment_address",
            )
            self.add_error("shipment", error)
