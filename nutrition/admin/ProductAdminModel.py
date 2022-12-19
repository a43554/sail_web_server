from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from nutrition.models.ProductModel import Product


# The admin for the product.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # The items to display in the list.
    list_display = ['product_name', 'ingredient_weight_in_grams', 'total_price', 'auto_validity', 'manual_validation', ]
    # Override the field for sources.
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    # Get the product name.
    def product_name(self, prod: Product):
        # Return the product name.
        return prod.ingredient.name
    # The description of the column.
    product_name.short_description = 'Name'

