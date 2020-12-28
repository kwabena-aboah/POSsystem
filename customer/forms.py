from django import forms
from . models import Customer


class CustomerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['orders'].widget.attrs.update({'class': 'form-control'})
        self.fields['amount_paid'].widget.attrs.update({'class': 'form-control'})
        self.fields['amount_to_pay'].widget.attrs.update({'class': 'form-control'})
        self.fields['payment_status'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Customer
        fields = ('name', 'phone', 'email', 'orders', 'amount_paid', 'amount_to_pay', 'payment_status')
