from django import forms

from .models import CategoryType, Category

# TODO:
#   -   Create these forms:
#       -   For filtering products in the catalog,
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


class CategoryFilterForm(forms.ModelForm):
    """A form for selecting categories defined in Category with separate
    fields for different ctg_type."""
    def __init__(self, *args, **kwargs):
        # set fields dynamically and hope this will work.
        ctg_types = CategoryType.objects.all()
        for ctg_type in ctg_types:
            setattr(
                self,
                ctg_type.name,
                forms.ModelMultipleChoiceField(
                    queryset=Category.objects.filter(ctg_type=ctg_type),
                    to_field_name="name",
                )
            )
        super().__init__(*args, **kwargs)

    # template_name is a property returning the value of
    # form_template_name of the renderer. It may be overridden like this:
    # template_name = "catalog_filter_snippet.html"
