from django.urls import path
from django.conf.urls import url
from django.views.generic import RedirectView
from  . import views

urlpatterns = [
    path('', views.listCustomer, name='list-client'),
    path('create/', views.createCustomer, name='customer'),
]