from django.db import models
from django.conf import settings
import os

class Participant(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    organization = models.CharField(max_length=150)
    title = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    workshop = models.CharField(max_length=150, default="Tax Workshop on TARMS")
    payment_method = models.CharField(max_length=50, default="bankTransfer")
    bank_name = models.CharField(max_length=100, blank=True)
    account_holder = models.CharField(max_length=100, blank=True)
    transaction_ref = models.CharField(max_length=100)
    payment_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    proof_of_payment = models.FileField(upload_to='proofs/')
    terms = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.full_name} ({self.email})"
        
    @property
    def proof_file_url(self):
        """Return the URL for the proof of payment file."""
        if not self.proof_of_payment:
            return None
            
        # In development, use the normal file URL
        if settings.DEBUG:
            return self.proof_of_payment.url
        
        # In production, use our custom URL pattern
        filename = os.path.basename(self.proof_of_payment.name)
        return f"/proofs/{filename}"
