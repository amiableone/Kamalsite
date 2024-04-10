from django import forms
from django.contrib.postgres.forms.ranges import IntegerRangeField
from django.core.exceptions import ValidationError
from django.db.models import Min, Max

from .models import Category, Like, Product

# TODO. Create these forms:
#   -   For filtering products in the catalog - DONE,
#   -   For sorting products in the catalog,
#   -   For adding a product to cart,
#   -   For liking/disliking a product,
#       -   Use sessions to disallow repeated likes, dislikes, additions
#           (this will be done in views).
#   -   For deleting products from cart,
#   -   For splitting products in cart,
#   -   For changing quantities of products in cart,
#       -   All of these operations with products in cart should be
#           preferrably done in a way that allows for recalculation of
#           the total price displayed right in the template (without
#           overhead of additional post requests).
#   -   For creating orders (e.g. by clicking on 'Buy' in a cart),
#   -   For filling out order details,
#       -   (Specify details of what forms are required here),


class PriceRangeField(forms.MultiValueField):
    """
    A field for specifying price range of Product instances through
    CategoryFilterForm.
    """
    # There's the IntegerRangeField in django.contrib.postgres
    # but I decided to create my own to feel it. My version compresses
    # the input to a simple tuple, not some fancy psycopg Range instance.
    # It's yet to see if it proves to be sufficient this way.

    def __init__(self, **kwargs):
        products = Product.objects.all()
        min_price = products.aggregate(min_price=Min("price"))["min_price"]
        max_price = products.aggregate(max_price=Max("price"))["max_price"]
        fields = (
            forms.IntegerField(
                min_value=min_price,
                initial=min_price,
            ),
            forms.IntegerField(
                max_value=max_price,
                initial=max_price,
            ),
        )
        super().__init__(
            fields=fields,
            require_all_fields=False,
            **kwargs,
        )

    def compress(self, data_list):
        if data_list[0] and data_list[1] and data_list[0] > data_list[1]:
            raise ValidationError(
                "Min price higher than Max price",
                code="min_gt_max",
            )
        return tuple(data_list)


class CategoryFilterForm(forms.Form):
    """
    A form for selecting categories defined in Category
    with separate fields for different ctg_type.
    """

    # Find out how to declare fields dynamically based on existing ctg_type
    # values. Using setattr in __init__ doesn't create the fields.
    colour = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(ctg_type="colour"),
        to_field_name="name",
        widget=forms.CheckboxSelectMultiple,
    )
    size = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(ctg_type="size"),
        to_field_name="name",
        widget=forms.CheckboxSelectMultiple,
    )
    # Replace with PriceRangeField or customize to account for existing
    # minimum and maximum prices of products.
    price_within = IntegerRangeField()

    # TODO. Add these fields:
    #   -   RangeFloat or RangeDecimal (custom field) for specifying price
    #       interval limits,
    #   -   Customize ModelMultipleChoiceField or SelectMultiple to allow for
    #       a neutral choice in addition to including/excluding. An alternative
    #       would be to create a separate form for excluding categories,

    # template_name is a property returning the value of form_template_name
    # of the renderer. It may be overridden like this:
    # template_name = "catalog_filter_snippet.html"


class LikeForm(forms.ModelForm):
    class Meta:
        model = Like
        fields = ["user", "product"]
        widgets = {
            "user": forms.HiddenInput,
            "product": forms.HiddenInput,
        }
