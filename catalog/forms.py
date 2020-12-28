from django import forms
from . models import Product  # , Order_Item


class ProductForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Product
        fields = ('name', 'price', 'selling_price', 'stock_applies', 'minimum_stock',
                  'stock', 'expiring_date', 'supplier', 'store', 'category', 'colour')


# class Order_ItemForm(forms.ModelForm):
#     class Meta:
#         model = Order_Item
#         fields = ['quantity']
