from django import forms

from .models import Category, Like

# TODO. Create these forms:
#   -   For filtering products in the catalog - DONE,
#   -   For sorting products in the catalog,
#   -   For adding a product to cart,
#   -   For liking/disliking a product,
#       - Use sessions to disallow repeated likes, dislikes, additions
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
