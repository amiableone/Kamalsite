from django import forms

from .models import Category

# TODO:
#   -   Create these forms:
#       -   For filtering products in the catalog,
#       -   For sorting products in the catalog,
#       -   For adding a product to cart,
#       -   For liking/disliking a product,
#           - Use sessions to disallow repeated likes, dislikes, additions
#       -   For deleting products from cart,
#       -   For splitting products in cart,
#       -   For changing quantities of products in cart,
#           -   All of these operations with products in cart should be
#               preferrably done in a way that allows for recalculation of
#               the total price displayed right in the template (without
#               overhead of additional post requests).
#       -   For creating orders (e.g. by clicking on 'Buy' in a cart),
#       -   For filling out order details,
#           -   (Specify details of what forms are required here),
#       -


class CategoryFilterForm(forms.Form):
    """A form for selecting categories defined in Category with separate
    fields for different ctg_type."""

    # Find out how to declare fields dynamically based on existing ctg_type
    # values. Using setattr in overridden __init__ doesn't create the fields.
    colour = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(ctg_type="colour"),
        to_field_name="name",
    )
    size = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(ctg_type="size"),
        to_field_name="name",
    )

    # template_name is a property returning the value of form_template_name
    # of the renderer. It may be overridden like this:
    # template_name = "catalog_filter_snippet.html"
