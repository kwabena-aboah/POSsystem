from django.contrib import admin
from . models import Customer
from . forms import CustomerForm


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'amount_paid', 'amount_to_pay', 'payment_status',)
    list_filter = ('payment_status',)
    search_fields = ('name',)
    form = CustomerForm
    list_per_page = 10

    # def save_model(self, request, obj, form, change):
    #     recieve_customer = Customer.objects.create(id=id)
    #     if getattr(obj, 'created_by', True) is not None:
    #         obj.created_by = request.user
    #         obj.save()
    #     recieve_customer.save()
    #     super().save_model(request, obj, form, change)


admin.site.register(Customer, CustomerAdmin)
