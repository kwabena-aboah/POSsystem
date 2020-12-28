import re
import time
from datetime import date, timedelta
from django.db import models
from django.dispatch import receiver
from plyer import notification
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.urls import reverse


def validate_name(names):
    regex_string = r'^\w[\w ]*$'
    search = re.compile(regex_string).search
    result = bool(search(names))
    if not result:
        raise ValidationError("Please only use letters, "
                              "numbers and underscores or spaces."
                              "The name cannot start with space.")


def validate_phone(phone):
    phone_regex = r'^\+?1?\d{9,15}$'
    search = re.compile(phone_regex).search
    result = bool(search(phone))
    if not result:
        raise RegexValidator("Phone numbers must be entered in the format:"
                             "'+999999999.' Up to 15 digits allowed.")


class Store(models.Model):
    """This class manages Store divisions, warehouses, diffrent branches etc. """
    name = models.CharField(max_length=150, validators=[validate_name])
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """This class manages the suppliers of the products"""
    name = models.CharField(max_length=100, validators=[validate_name])
    email = models.EmailField(blank=True)
    tel = models.CharField(max_length=17, validators=[
                           validate_phone], blank=True)
    location = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, validators=[validate_name])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Product(models.Model):
    """ This class manages information related to the products."""
    # The different colours, to use as Product.<colour>
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    PURPLE = "purple"
    BLACK = "black"
    PINK = "pink"
    CYAN = "cyan"

    # Colour choices
    COLOUR_CHOICES = (
        (BLUE, "Blue"),
        (GREEN, "Green"),
        (YELLOW, "Yellow"),
        (ORANGE, "Orange"),
        (PURPLE, "Purple"),
        (BLACK, "Black"),
        (PINK, "Pink"),
        (CYAN, "Cyan"),
    )
    name = models.CharField(max_length=200, validators=[validate_name])
    price = models.DecimalField(max_digits=7, decimal_places=2)
    stock_applies = models.BooleanField()
    selling_price = models.DecimalField(max_digits=7, decimal_places=2)
    minimum_stock = models.PositiveSmallIntegerField(default=0)
    stock = models.IntegerField(default=0)
    expiring_date = models.DateField()
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, blank=True, null=True, related_name='product_supplier')
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, blank=True, null=True, related_name="product_store")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, null=True, related_name="product_category")
    colour = models.CharField(
        max_length=10, choices=COLOUR_CHOICES, default="blue")
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

    def expired_field(self):
        if date.today() >= self.expiring_date:
            return format_html(u'<span style="color: red;">Expired</span>')
    expired_field.allow_tags = True

    def stock_level(self):
        if self.stock <= self.minimum_stock:
            return format_html(u"<span style='color: red;'>Low</span>")
        else:
            return format_html(u"<span style='color: green;'>High</span>")
    stock_level.allow_tags = True


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    done = models.BooleanField(default=False)
    last_change = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('view_order', args=[self.id])

    def get_total_cost(self):
        """ Calculate total order cost for orders"""
        return sum(item.get_cost() for item in self.items.all())

    def count_quantity(self):
        """ Count for the quantity of order_items needed by customer."""
        result = 0
        for item in self.items.all():
            result += 1 * item.quantity
        return result


class Cash(models.Model):
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    def __str__(self):
        return self.amount

    class Meta:
        verbose_name = 'Cash'
        verbose_name_plural = 'Cash'


class Order_Item(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.IntegerField(default=1)
    name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name

    def get_cost(self):
        return self.price * self.quantity


class Setting(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.key

    def __bool__(self):
        return bool(self.value)

    __nonzero__ = __bool__
