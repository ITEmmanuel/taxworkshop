from django.shortcuts import render
from datetime import datetime
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import os

def home(request):
    context = {
        'current_year': datetime.now().year
    }
    return render(request, 'home.html', context)

class RegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=100, label='Full Name')
    email = forms.EmailField(label='Email')
    bank = forms.CharField(max_length=100, label='Paying Bank')
    from_account = forms.CharField(max_length=50, label='From Account Number')
    payment_date = forms.DateField(label='Payment Date', widget=forms.DateInput(attrs={'type': 'date'}))
    proof = forms.FileField(label='Proof of Payment')

from .models import Participant

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            participant = Participant(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                bank=form.cleaned_data['bank'],
                from_account=form.cleaned_data['from_account'],
                payment_date=form.cleaned_data['payment_date'],
                proof=form.cleaned_data['proof']
            )
            participant.save()
            return render(request, 'register_success.html', {'name': form.cleaned_data['full_name']})
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})
