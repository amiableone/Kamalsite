from django import forms
from django.contrib.postgres.forms.ranges import IntegerRangeField
from django.core.exceptions import ValidationError
from django.db.models import Min, Max, TextChoices
from django.utils.translation import gettext_lazy as _

from .models import Addition, Category, Like, Product

# TODO.
#   -   Create these forms:
#       -   For filtering products in the catalog - DONE,
#       -   For sorting products in the catalog - DONE,
#       -   For liking/disliking a product - DONE,
#           -   Use sessions to disallow repeated likes/dislikes, additions
#               (this will be done in views).
#       -   For adding a product to cart - DONE,
#       -   For deleting products from cart,
#       -   For adding a 'leave in cart after purchase' checkbox to products
#           in cart,
#       -   For changing quantities of products in cart,
#           -   All of these operations with products in cart should be
#               preferrably done in a way that allows for recalculation of
#               the total price displayed right in the template (without
#               overhead of additional post requests).
#       -   For creating orders (e.g. by clicking on 'Buy' in a cart),
#       -   For filling out order details,
#           -   (Specify details of what forms are required here),
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
        lo, hi = data_list[0], data_list[1]
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
        # Pass initial values to these fields from the corresponding view.
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
    Initiate with an Addition instance.
    """

    class Meta(AdditionForm.Meta):
        fields = AdditionForm.Meta.fields + ["quantity"]

    def __init__(self, *args, **kwargs):
        if not "instance" in kwargs:
            raise KeyError("Provide instance to __init__")
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        data = self.cleaned_data
        product = self.instance.product
        available = product.quantity
        minimum = product.min_order_quantity
        if available < data["quantity"] < minimum:
            message = _("Please limit your order quantity to %(available)s "
                        "%(units)s (available) or order %(minimum)s %(units)s "
                        "(minimum order quantity).")
            raise ValidationError(
                message,
                code="invalid_quantity",
                params={
                    "available": available,
                    "minimum": minimum,
                    "units": product.unit_measure,
                }
            )
        return data


class DeleteAdditionForm(AdditionForm):
    """
    Delete product from cart (by setting Addition.quantity to zero).
    """

    def save(self, commit=True):
        addition = super().save(commit=False)
        addition.quantity = 0
        if commit:
            addition.save()
        return addition
