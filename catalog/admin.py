from datetime import date
import datetime
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import F
from import_export import resources
from . models import Store, Supplier, Category, Product, Order, Cash, Setting
from import_export.admin import ImportExportModelAdmin
from . forms import ProductForm


admin.site.disable_action('delete_selected')

admin.site.site_header = "JKF-VICTORY LIMITED"
admin.site.site_title = "JKF-VICTORY LIMITED ADMINISTRATION"
admin.site.index_title = "JKF-VICTORY LIMITED ADMINISTRATION"
admin.site.site_url = "/"


class ProductResource(resources.ModelResource):

    class Meta:
        model = Product
        fields = (
            'name',
            'price',
            'selling_price',
            'stock',
            'stock_applies',
            'minimum_stock',
            'expiring_date',
            'stock_level'
        )


class LowStockFilter(SimpleListFilter):
    title = 'Available Stock'
    parameter_name = 'available_stock'

    def lookups(self, request, model_admin):
        return (
            ('low', 'Low Stock'),
            ('high', 'High Stock')
        )

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(stock__lte=F('minimum_stock'))
        if self.value() == 'high':
            return queryset.filter(stock__gte=F('minimum_stock'))


class ExpiredStockFilter(SimpleListFilter):
    title = 'Expired Stock'
    parameter_name = 'expired_stock'

    def lookups(self, request, model_admin):
        return (
            ('expired', 'Expired Product'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'expired':
            return queryset.filter(expiring_date__lte=datetime.datetime.today())


class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')


admin.site.register(Setting, SettingAdmin)


class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    actions = ['delete_selected']
    resource_class = ProductResource
    list_display = (
        'expired_field',
        'name',
        'price',
        'selling_price',
        'stock',
        'stock_applies',
        'minimum_stock',
        'expiring_date',
        'stock_level'
    )

    list_display_links = ('name',)
    search_fileds = ('name',)
    date_hierarchy = 'created_on'
    form = ProductForm
    list_per_page = 10

    list_filter = (LowStockFilter, ExpiredStockFilter,)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', True) is not None:
            obj.created_by = request.user
            obj.save()
        super().save_model(request, obj, form, change)


admin.site.register(Product, ProductAdmin)


class StoreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    search_fileds = ('code',)
    actions = ['delete_selected']
    list_per_page = 5


admin.site.register(Store, StoreAdmin)

admin.site.register(Category)


class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'tel', 'location', 'comments')
    list_display_links = ('name',)
    search_fileds = ('name', 'email',)
    actions = ['delete_selected']
    list_per_page = 10


admin.site.register(Supplier, SupplierAdmin)

# Safe deletion of orders


def safe_delete_order(modeladmin, request, queryset):
    queryset.filter(done=True).delete()


safe_delete_order.short_description = "Delete completed orders"


class OrderAdmin(admin.ModelAdmin):
    ''' Admin site configuration for Order Model'''
    # Add custom delete-if-not-done action
    actions = [safe_delete_order]
    # List page display configuration
    list_display = ('user', 'total_price', 'done', 'last_change')
    # sidebar filter configuration
    list_filter = ('done',)
    date_hierarchy = 'last_change'
    # order by not Done
    ordering = ('done',)
    list_per_page = 10


admin.site.register(Order, OrderAdmin)

admin.site.register(Cash)
