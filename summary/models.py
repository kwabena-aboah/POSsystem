from django.db import models
from catalog.models import Order, Order_Item


class OrderSummary(Order):
    class Meta:
        proxy = True
        verbose_name = 'Order Report'
        verbose_name_plural = 'Order Reports'


class OrderItemSummary(Order_Item):
    class Meta:
        proxy = True
        verbose_name = "Product Report"
        verbose_name_plural = "Product Reports"
