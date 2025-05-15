from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
import os
import requests

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
                phone=form.cleaned_data['phone'],
                organization=form.cleaned_data['organization'],
                title=form.cleaned_data['title'],
                city=form.cleaned_data['city'],
                country=form.cleaned_data['country'],
                workshop=form.cleaned_data['workshop'],
                payment_method=form.cleaned_data['payment_method'],
                bank_name=form.cleaned_data['bank_name'],
                account_holder=form.cleaned_data['account_holder'],
                transaction_ref=form.cleaned_data['transaction_ref'],
                payment_date=form.cleaned_data['payment_date'],
                amount_paid=form.cleaned_data['amount_paid'],
                proof_of_payment=form.cleaned_data['proof_of_payment'],
                terms=form.cleaned_data['terms'],
            )
            participant.save()
            return render(request, 'register_success.html', {'name': participant.full_name})
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    # Filtering
    org = request.GET.get('organization', '')
    payment_date = request.GET.get('payment_date', '')
    participants = Participant.objects.all()
    if org:
        participants = participants.filter(organization__icontains=org)
    if payment_date:
        participants = participants.filter(payment_date=payment_date)
    participants = participants.order_by('-registered_at')
    orgs = Participant.objects.values_list('organization', flat=True).distinct()
    return render(request, 'dashboard.html', {
        'participants': participants,
        'orgs': orgs,
        'selected_org': org,
        'selected_date': payment_date
    })

@login_required
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

@login_required
def dashboard_delete(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    if request.method == 'POST':
        participant.delete()
        return redirect('dashboard')
    return render(request, 'register.html', {'form': None, 'delete_confirm': True, 'participant': participant})

@login_required
def dashboard_payment_action(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            participant.payment_status = 'approved'
            subject = 'Payment Approved - Tax Workshop'
            message = f"Dear {participant.full_name},\n\nYour payment for the Tax Workshop has been approved. See you on the event date!\n\nBest regards,\nTax Workshop Team"
        elif action == 'decline':
            participant.payment_status = 'declined'
            subject = 'Payment Declined - Tax Workshop'
            message = f"Dear {participant.full_name},\n\nUnfortunately, your payment could not be confirmed. Please re-register or confirm with your bank as payment does not appear to have been received.\n\nBest regards,\nTax Workshop Team"
        else:
            return redirect('dashboard')
        participant.save()
        # Send email via Resend API
        resend_api_key = os.environ.get('RESEND_API_KEY')
        if resend_api_key:
            try:
                response = requests.post(
                    'https://api.resend.com/emails',
                    headers={
                        'Authorization': f'Bearer {resend_api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'from': 'noreply@taxworkshop.com',
                        'to': [participant.email],
                        'subject': subject,
                        'text': message
                    },
                    timeout=10
                )
                response.raise_for_status()
            except Exception as e:
                print(f"Failed to send email: {e}")
        return redirect('dashboard')
    return redirect('dashboard')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


from django.contrib import messages

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('password_change_done')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password_change.html', {'form': form})


@login_required
def password_change_done_view(request):
    return render(request, 'password_change_done.html')
