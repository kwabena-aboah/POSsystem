import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from catalog.models import Order_Item
from django.contrib.auth.models import User


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


class Customer(models.Model):
    PAID = 'Paid'
    PART = 'Part Payment'
    STATUS = (
        (PAID, 'Paid'),
        (PART, 'Part Payment'),
    )
    name = models.CharField(max_length=200, null=True,
                            validators=[validate_name])
    phone = models.CharField(max_length=17, null=True,
                             validators=[validate_phone], blank=True)
    email = models.EmailField(blank=True, null=True)
    orders = models.ManyToManyField(Order_Item)
    amount_to_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=14, choices=STATUS, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     for order in self.orders:
    #         if self.amount == order.price:
    #             return self.payment_status.Paid
    #         else:
    #             return self.payment_status.PART
    #     return super(Customer, self).save(*args, **kwargs)
