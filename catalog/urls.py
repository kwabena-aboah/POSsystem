from django.urls import path
from django.conf.urls import url
from django.views.generic import RedirectView
from . import views
from . import apiviews

# app_name = "catalog"
urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='order')),
    path('', views.order, name='order'),
    path('addition/', views.addition, name='addition'),
    url(r'^order/add/(?P<product_id>[0-9A-Za-z_-]*/?$)',
        views.order_add_product, name='order_add_product'),
    url(r'^order/remove/(?P<product_id>[0-9]*)/?$',
        views.order_remove_product, name="order_remove_product"),
    url(r'^order/reset/?$', views.reset_order, name='reset_order'),
    url(r'^order/amount/?$', views.order_amount, name='order_get_amount'),
    url(r'^order/?$', views.order, name='order'),

    url(r'^pay/momo/$', views.payment_momo, name='payment_momo'),
    url(r'^pay/cash/$', views.payment_cash, name='payment_cash'),

    path('cash/<int:amount>/', views.cash, name='cash'),

    url(r'^view-order/(?P<order_id>[0-9]+)/?$', views.view_order,
        name='view_order'),
    url(r'^print-order/(?P<order_id>[0-9]+)/?$', views.print_order,
        name='print_order'),
    url(r'^print-current-order/?$', views.print_current_order,
        name='print_current_order'),

    url(r'^stock/?$', views.view_stock, name='view_stock'),

    # API URL's
    path('api/orders/current/', apiviews.current_order,
         name='api_current_order'),
    path('api/orders/current/items/', apiviews.current_order_items,
         name='api_current_order_items'),
    path('api/orders/current/items/<int:item_id>/',
         apiviews.current_order_item,
         name='api_product'),
    path('api/orders/current/items/patch/<int:item_id>/',
         apiviews.current_order_patch, name='api_current_order_patch'),
    path('api/orders/current/items/search/<str:item_id>/',
         apiviews.search_order_item, name='api_search_product'),
    path('api/pay/momo/', apiviews.momo_payment, name='api_momo_payment'),
    path('api/pay/cash/', apiviews.cash_payment, name='api_cash_payment'),
]
