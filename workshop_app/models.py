from django.db import models

from django.db import models

class Participant(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    bank = models.CharField(max_length=100)
    from_account = models.CharField(max_length=50)
    payment_date = models.DateField()
    proof = models.FileField(upload_to='proofs/')
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.email})"
