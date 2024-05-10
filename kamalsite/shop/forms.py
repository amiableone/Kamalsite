from django import forms
from django.contrib.postgres.forms.ranges import IntegerRangeField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import F, Min, Max, TextChoices
from django.utils.translation import gettext_lazy as _

from .models import (
    Addition,
    Category,
    Like,
    Order,
    OrderDetail,
    Product,
    Shipment,
)

# TODO.
#   -   Create a bug report for:
#       -   Product.objects.filter(price__contained_by=nr) - where nr is a
#           NumericRange instance - raises django.core.exceptions.FieldError:
#           Unsupported lookup 'contained_by' for DecimalField or join on the
#           field not permitted (even when nr is based on Decimal values).
#           The documentation says contained_by supports DecimalField.


class RangeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = {
            "min": forms.NumberInput,
            "max": forms.NumberInput,
        }
        super().__init__(widgets=widgets, attrs=attrs)

    def decompress(self, value):
        if value:
            return [i for i in value]
        return [None, None]


def get_price_extremes():
    extremes = Product.objects.filter(in_production=True).aggregate(
        min=Min("price"),
        max=Max("price"),
    )
    return extremes["min"], extremes["max"]


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
        lo, hi = get_price_extremes()
        fields = (
            forms.IntegerField(
                min_value=lo,
                required=False,
            ),
            forms.IntegerField(
                max_value=hi,
                required=False,
            ),
        )
        super().__init__(
            fields=fields,
            require_all_fields=False,
            required=False,
            widget=RangeWidget,
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


def get_category_types():
    types = Category.objects.values("name").distinct()
    names = [t["name"] for t in types]
    processed = {}

    def process(item):
        if processed.get(item):
            return False
        processed[item] = True
        return True

    return list(filter(process, names))


class CatalogFilterForm(forms.Form):
    """
    A form for filtering products in the catalog.
    Each Category.ctg_type uses a separate ModelMultipleChoiceField.
    """

    action = forms.CharField(initial="filter_catalog", widget=forms.HiddenInput)
    types = forms.MultipleChoiceField(
        initial=get_category_types,
        widget=forms.MultipleHiddenInput,
    )
    retail = forms.BooleanField(
        help_text="Limit to products available for retail purchase.",
        initial=False,
        required=False,
    )
    price_range = PriceRangeField(initial=get_price_extremes)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        names = self.fields["types"].initial()
        for name in names:
            self.fields[name] = forms.ModelMultipleChoiceField(
                queryset=Category.objects.filter(name=name),
                required=False,
                to_field_name="value",
                widget=forms.CheckboxSelectMultiple,
            )


class CatalogSortForm(forms.Form):
    """
    A form for sorting products in the catalog.
    """

    class SortBy(TextChoices):
        NAME = "name", _("Name")
        POPULARITY = "popularity", _("Popularity")
        PRICE = "price", _("Price")
        NOVELTY = "novelty", _("Novelty")

    action = forms.CharField(initial="sort_catalog", widget=forms.HiddenInput)
    sort_by = forms.ChoiceField(
        choices=SortBy,
        initial=SortBy.NOVELTY,
    )
    ascending = forms.BooleanField(
        initial=False,
        required=False,
    )


class LikeForm(forms.ModelForm):
    """
    Like a product.
    """
    action = forms.CharField(initial="like", widget=forms.HiddenInput)

    class Meta:
        model = Like
        fields = []

    def save(self, commit=True):
        # Provide Like instance to the bound form.
        like = super().save(commit=False)
        if commit:
            like.liked = ~F("liked")
            like.save()
            like.refresh_from_db(fields=["liked"])
        return like


class AdditionForm(forms.ModelForm):
    action = forms.CharField(initial="addition", widget=forms.HiddenInput)

    class Meta:
        model = Addition
        fields = ["product"]
        widgets = {
            "product": forms.HiddenInput,
        }


class CreateAdditionForm(AdditionForm):
    """
    Add products to cart with this form.
    Create a new Addition instance or update an existing one.
    """

    def save(self, commit=True):
        # Provide Addition instance to the bound form.
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

    def __init__(self, *args, **kwargs):
        if not "instance" in kwargs:
            raise TypeError("instance argument is required.")
        super().__init__(*args, **kwargs)

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
        if not kwargs["initial"]["from_cart"] and not product:
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
                    )
                    for a in order_now
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
            try:
                first, middle, last = value.split(" ")
                return  [last, first, middle]
            except ValueError:
                first, last = value.split(" ")
                return  [last, first, None]
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
        full_name = first, middle, last
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
            "as_individual",
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
            "receiver": FullNameField,
            "shipped": forms.NullBooleanField,
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
                order.as_individual = True
                order.purchaser = user.get_full_name()
            order.purchaser_email = user.email
        super().__init__(*args, **kwargs)
        self.fields["user"].disabled = True
        self.fields["shipped"].required = False
        self.fields["shipment"].required = False
        self.fields["shipment"].queryset = Shipment.objects.filter(user=user)
        self.fields["shipment"].to_field_name = "address"
        # self.fields["shipment_company"].required = False

    def clean(self):
        super().clean()
        data = self.cleaned_data
        if data["shipped"] and not data["shipment"]:
            error = ValidationError(
                message=_("Shipment address is not specified."),
                code="empty_shipment_address",
            )
            self.add_error("shipment", error)

    def save(self, commit=True):
        order = super().save(commit=False)
        if commit:
            if self.is_valid():
                # Move this operation to a view or form that manages email
                # confirmation. commit=True is required because the form may be
                # valid but still incomplete when shipped=False.
                order.confirmed = True
                order.make_purchase()
            order.save()
        return order


class AddressWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = {
            "country": forms.TextInput,
            "area": forms.TextInput,
            "city": forms.TextInput,
            "street": forms.TextInput,
            "building": forms.TextInput,
        }
        super().__init__(widgets=widgets, attrs=attrs)

    def decompress(self, value):
        if isinstance(value, str):
            return value.split(", ")
        return [None for w in self.widgets]


class AddressField(forms.MultiValueField):
    """
    A field for specifying an address.
    """

    def __init__(self, max_length=None, **kwargs):
        fields = (
            forms.CharField(
                error_messages={"incomplete": "Enter a country name."},
                initial=_("Russia"),
                max_length=20,
            ),
            forms.CharField(
                initial=_("(Optional)"),
                max_length=40,
                required=False,
            ),
            forms.CharField(
                error_messages={"incomplete": "Enter a city name."},
                initial=_("Moscow"),
                max_length=40,
            ),
            forms.CharField(
                error_messages={"incomplete": "Enter a street name."},
                max_length=40,
            ),
            forms.CharField(
                error_messages={"incomplete": "Enter a valid building number."},
                max_length=10,
            ),
        )
        super().__init__(
            fields=fields,
            require_all_fields=False,
            widget=AddressWidget,
            **kwargs,
        )

    def compress(self, data_list):
        if data_list:
            return ", ".join(data_list)
        return None


class ShipmentForm(forms.ModelForm):
    """
    A form for creating shipment address objects.
    """
    save_address = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = Shipment
        fields = ["user", "address", "zip"]
        field_classes = {"address": AddressField}
        widgets = {"user": forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].disabled = True
        self.fields["zip"].validators = [
            RegexValidator(r"^[0-9]{5,6}$", "Enter a valid zip code."),
        ]
