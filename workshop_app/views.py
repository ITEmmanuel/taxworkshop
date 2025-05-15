from django.shortcuts import render, get_object_or_404, redirect
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
    email = forms.EmailField(label='Email Address')
    phone = forms.CharField(max_length=30, label='Phone Number', required=False)
    organization = forms.CharField(max_length=150, label='Organization/Institution')
    title = forms.CharField(max_length=100, label='Job Title/Position')
    city = forms.CharField(max_length=100, label='City/Town', required=False)
    country = forms.CharField(max_length=100, label='Country', required=False)
    workshop = forms.CharField(max_length=150, initial='Tax Workshop on TARMS', widget=forms.HiddenInput())
    payment_method = forms.CharField(max_length=50, initial='bankTransfer', widget=forms.HiddenInput())
    bank_name = forms.CharField(max_length=100, label='Bank Name', required=False)
    account_holder = forms.CharField(max_length=100, label='Account Holder Name', required=False)
    transaction_ref = forms.CharField(max_length=100, label='Transaction Reference Number/Deposit Slip Number')
    payment_date = forms.DateField(label='Date of Payment', widget=forms.DateInput(attrs={'type': 'date'}))
    amount_paid = forms.DecimalField(label='Amount Paid (ZWL)', max_digits=12, decimal_places=2)
    proof_of_payment = forms.FileField(label='Proof of Payment (JPG, PNG, PDF)')
    terms = forms.BooleanField(label='I agree to the terms and conditions')

from .models import Participant

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            participant = Participant(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data.get('phone', ''),
                organization=form.cleaned_data['organization'],
                title=form.cleaned_data['title'],
                city=form.cleaned_data.get('city', ''),
                country=form.cleaned_data.get('country', ''),
                workshop=form.cleaned_data['workshop'],
                payment_method=form.cleaned_data['payment_method'],
                bank_name=form.cleaned_data.get('bank_name', ''),
                account_holder=form.cleaned_data.get('account_holder', ''),
                transaction_ref=form.cleaned_data['transaction_ref'],
                payment_date=form.cleaned_data['payment_date'],
                amount_paid=form.cleaned_data['amount_paid'],
                proof_of_payment=form.cleaned_data['proof_of_payment'],
                terms=form.cleaned_data['terms']
            )
            participant.save()
            return render(request, 'register_success.html', {'name': form.cleaned_data['full_name']})
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def dashboard(request):
    participants = Participant.objects.all().order_by('-registered_at')
    return render(request, 'dashboard.html', {'participants': participants})

def dashboard_edit(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            for field in form.cleaned_data:
                setattr(participant, field, form.cleaned_data[field])
            if 'proof_of_payment' in request.FILES:
                participant.proof_of_payment = request.FILES['proof_of_payment']
            participant.save()
            return redirect('dashboard')
    else:
        initial = {field: getattr(participant, field) for field in RegistrationForm.base_fields}
        form = RegistrationForm(initial=initial)
    return render(request, 'register.html', {'form': form, 'edit_mode': True, 'participant': participant})

def dashboard_delete(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    if request.method == 'POST':
        participant.delete()
        return redirect('dashboard')
    return render(request, 'register.html', {'form': None, 'delete_confirm': True, 'participant': participant})
