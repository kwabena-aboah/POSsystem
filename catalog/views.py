import logging
import decimal
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404#, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, HttpResponseRedirect)
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from . models import Product, Order, Cash, Order_Item
from . tasks import expiry_date, expired, stock_level
from . import helper


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                messages.success(request, "Login Successful")
                auth_login(request, user)
                return HttpResponseRedirect(reverse('order'))
            else:
                return messages.info(request, "Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(
                username, password))
            messages.error(request, "Invalid login details given")
            return HttpResponseRedirect('/')
    else:
        return render(request, 'registration/login.html', {'title': 'LOGIN PAGE'})


@login_required
def order(request):
    # Sort products by code, then by name
    list = Product.objects.order_by('name')
    currency = helper.get_currency()
    expiry_day = expiry_date()
    expired_today = expired()
    stock_level_info = stock_level()
    context = {
        'list': list,
        'currency': currency,
        'expiry_day': expiry_day,
        'expired_today': expired_today,
        'stock_level_info': stock_level_info,
        'title': 'Orders',
    }
    return render(request, 'inventory/index.html', context=context)


def _addition_no_stock(request):
    cash, current_order, currency = helper.setup_handling(request)

    total_price = current_order.total_price
    list = Order_Item.objects.filter(order=current_order)
    context = {
        'list': list,
        'total_price': total_price,
        'cash': cash,
        'succesfully_payed': False,
        'payment_error': False,
        'amount_added': 0,
        'currency': currency,
        'stock_error': True,
    }
    return render(request, 'inventory/addition.html', context=context)


@login_required
def addition(request):
    cash, current_order, currency = helper.setup_handling(request)

    total_price = current_order.total_price
    list = Order_Item.objects.filter(order=current_order)
    context = {
        'list': list,
        'total_price': total_price,
        'cash': cash,
        'succesfully_payed': False,
        'payment_error': False,
        'amount_added': 0,
        'currency': currency,
        'stock_error': False,
    }
    return render(request, 'inventory/addition.html', context=context)


def _show_order(request, order_id, should_print):
    currency = helper.get_currency()
    order = get_object_or_404(Order, id=order_id)
    items = Order_Item.objects.filter(order=order)
    company = helper.get_company()

    context = {
        'list': items,
        'order': order,
        'currency': currency,
        'company': company,
        'print': should_print
    }

    return render(request, 'inventory/view_order.html', context=context)


@login_required
def view_order(request, order_id):
    return _show_order(request, order_id, False)


@login_required
def print_order(request, order_id):
    return _show_order(request, order_id, True)


@login_required
def print_current_order(request):
    # Get the user. This is quite a roundabout, sorry
    usr = User.objects.get_by_natural_key(request.user.username)
    q = Order.objects.filter(user=usr)\
                     .order_by('-last_change')

    # This is an edge case that would pretty much never occur
    if q.count() < 1:
        return HttpResponseBadRequest
    return _show_order(request, q[0].id, True)


@login_required
def order_amount(request):
    _, current_order, _ = helper.setup_handling(request)
    return HttpResponse(current_order.total_price)


@login_required
def order_add_product(request, product_id):
    _, current_order, _ = helper.setup_handling(request)

    if product_id.isdigit():
        try:
            to_add = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            to_add = get_object_or_404(Product, code=product_id)

    else:
        to_add = get_object_or_404(Product, code=product_id)

    # Make sure we can't go under 0 stock
    if to_add.stock_applies:
        if to_add.stock < 1 and not helper.get_can_negative_stock():
            return _addition_no_stock(request)

        to_add.stock -= 1
        to_add.save()

    Order_Item.objects.create(order=current_order, product=to_add,
                              price=to_add.price, name=to_add.name)
    current_order.total_price = current_order.get_total_cost()
    current_order.save()

    return addition(request)


@login_required
def order_remove_product(request, product_id):
    cash, current_order, _ = helper.setup_handling(request)
    order_item = get_object_or_404(Order_Item, id=product_id)
    order_product = order_item.product

    if order_product.stock_applies:
        order_product.stock += 1
        order_product.save()

    current_order.total_price = current_order.get_total_cost()

    if current_order.total_price < 0:
        logging.error("prices below 0! "
                      "You might be running in to the "
                      "10 digit total order price limit")
        current_order.total_price = 0

    current_order.save()
    order_item.delete()

    # I only need default values.
    return addition(request)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def reset_order(request):
    cash, current_order, _ = helper.setup_handling(request)

    for item in Order_Item.objects.filter(order=current_order):
        if item.product.stock_applies:
            item.product.stock += item.product.quantity
            item.product.save()
        item.delete()

    current_order.total_price = 0
    current_order.save()

    # I just need default values. Quite useful
    return addition(request)


@login_required
def payment_cash(request):
    succesfully_payed = False
    payment_error = False
    amount_added = 0
    cash, current_order, currency = helper.setup_handling(request)

    for product in helper.product_list_from_order(current_order):
        cash.amount += product.price * product.quantity
        amount_added += product.price * product.quantity
        cash.save()

    current_order.done = True
    current_order.save()
    current_order = Order.objects.create(user=request.user)
    succesfully_payed = True

    total_price = current_order.total_price
    list = Order_Item.objects.filter(order=current_order)
    context = {
        'list': list,
        'total_price': total_price,
        'cash': cash,
        'succesfully_payed': succesfully_payed,
        'payment_error': payment_error,
        'amount_added': amount_added,
        'currency': currency,
    }
    return render(request, 'inventory/addition.html', context=context)


@login_required
def payment_momo(request):
    succesfully_payed = False
    payment_error = False
    cash, current_order, currency = helper.setup_handling(request)

    current_order.done = True
    current_order.save()
    current_order = Order.objects.create(user=request.user)
    succesfully_payed = True

    total_price = current_order.total_price
    list = Order_Item.objects.filter(order=current_order)
    context = {
        'list': list,
        'total_price': total_price,
        'cash': cash,
        'succesfully_payed': succesfully_payed,
        'payment_error': payment_error,
        'amount_added': 0,
        'currency': currency,
    }
    return render(request, 'inventory/addition.html', context=context)


# We can't use the `@login_required` decorator here because this
# page is never shown to the user and only used in AJAX requests
def cash(request, amount):
    if (request.user.is_authenticated):
        cash, _ = Cash.objects.get_or_create(id=0)
        cash.amount = amount
        cash.save()
        return HttpResponse('')
    else:
        return HttpResponseForbidden('403 Forbidden')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def view_stock(request):
    stock_products = Product.objects.filter(stock_applies=True)
    company = helper.get_company()

    context = {
        'list': stock_products,
        'company': company
    }

    return render(request, 'inventory/stock.html', context=context)
