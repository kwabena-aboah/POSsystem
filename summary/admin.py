from django.contrib import admin
from django.db.models import Count, Sum, Min, Max, DateTimeField
from django.db.models.functions import Trunc

from . import models


def get_next_in_date_hierarchy(request, date_hierarchy):
    if date_hierarchy + '__day' in request.GET:
        return 'hour'
    if date_hierarchy + '__month' in request.GET:
        return 'day'
    if date_hierarchy + '__year' in request.GET:
        return 'week'
    return 'month'


@admin.register(models.OrderSummary)
class LoadOrderSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/order_change_list.html'
    actions = None
    date_hierarchy = 'last_change'
    show_full_result_count = False

    list_filter = (
        'user__username',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        # list view
        metrics = {
            'total': Count('id'),
            'total_cost': Sum('total_price')
        }

        response.context_data['summary'] = list(
            qs
                .values('id', 'total_price')
                .annotate(**metrics)
                .order_by('-last_change')
        )

        # list view summary
        response.context_data['summary_total'] = dict(qs.aggregate(**metrics))

        # Chart
        period = get_next_in_date_hierarchy(request, self.date_hierarchy)
        response.context_data['period'] = period
        summary_over_time = qs.annotate(
            period=Trunc('last_change', 'day', output_field=DateTimeField()),
        ).values('id').annotate(total=Sum('total_price')).order_by('last_change')

        summary_range = summary_over_time.aggregate(
            low=Min('total'),
            high=Max('total'),
        )
        high = summary_range.get('high', 0)
        low = summary_range.get('low', 0)

        response.context_data['summary_over_time'] = [{
            'period': x['id'],
            'total': x['total'] or 0,
            'pct': ((x['total'] or 0) - low) / (high - low) * 100
            if high > low else 0,
        } for x in summary_over_time]

        return response


@admin.register(models.OrderItemSummary)
class LoadOrderItemSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/orderitem_change_list.html'
    actions = None
    date_hierarchy = 'timestamp'
    show_full_result_count = False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        # list view
        metrics = {
            'total_product': Count('product__name'),
            'total_price': Sum('price')
        }

        response.context_data['summary'] = list(
            qs
            .values('product__name', 'price')
            .annotate(**metrics)
            .order_by('-timestamp')
        )

        # list view summary
        response.context_data['summary_total'] = dict(qs.aggregate(**metrics))

        # Chart
        period = get_next_in_date_hierarchy(request, self.date_hierarchy)
        response.context_data['period'] = period
        summary_over_time = qs.annotate(
            period=Trunc('timestamp', 'day', output_field=DateTimeField()),
        ).values('product__name').annotate(total=Sum('price')).order_by('timestamp')

        summary_range = summary_over_time.aggregate(
            low=Min('total'),
            high=Max('total'),
        )
        high = summary_range.get('high', 0)
        low = summary_range.get('low', 0)

        response.context_data['summary_over_time'] = [{
            'period': x['product__name'],
            'total': x['total'] or 0,
            'pct': ((x['total'] or 0) - low) / (high - low) * 100
            if high > low else 0,
        } for x in summary_over_time]

        return response
