from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Customer
# from catalog import helper
from . forms import CustomerForm

@login_required
def createCustomer(request):
    if request.method != 'POST':
        form = CustomerForm()
    else:
        form = CustomerForm(request.POST)
        if form.is_valid():
            new_customer = form.save(commit=False)
            new_customer.created_by = request.user
            new_customer.save()
            messages.success(request, "Record successfully added!")
            return redirect('/')
    context = {'form': form, 'title': 'Create Customer'}
    return render(request, 'customer/index.html', context)

@login_required
def listCustomer(request):
    customers = Customer.objects.all()
    title = "Manage Creditors"
    context = {'customers': customers, 'title': title}
    return render(request, 'customer/creditor.html', context)
