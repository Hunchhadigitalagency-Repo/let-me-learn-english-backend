from django.db import models
from user.models import School
# Create your models here.
class SubscriptionHistory(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("inactive", "Inactive"),
        ("deactivated", "Deactivated"),
    )

    PAYMENT_MODE_CHOICES = (
        ("cash", "Cash"),
        ("online", "Online"),
        ("bank", "Bank Transfer"),
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    package = models.CharField(max_length=255)

    remarks = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    payment_mode = models.CharField(
        max_length=50,
        choices=PAYMENT_MODE_CHOICES
    )

    amount = models.PositiveIntegerField()

    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.school} - {self.package} ({self.status})"



from django.db import models
from school.models import SubscriptionHistory
from user.models import School
from django.contrib.auth import get_user_model

User = get_user_model()

class SubscriptionLog(models.Model):
    subscription = models.ForeignKey(
        SubscriptionHistory, 
        on_delete=models.CASCADE, 
        related_name="logs"
    )
    school = models.ForeignKey(
        School, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The user who made the change"
    )
    old_status = models.CharField(max_length=255, blank=True, null=True)
    new_status = models.CharField(max_length=255, blank=True, null=True)
    old_amount = models.PositiveIntegerField(blank=True, null=True)
    new_amount = models.PositiveIntegerField(blank=True, null=True)
    old_payment_mode = models.CharField(max_length=50, blank=True, null=True)
    new_payment_mode = models.CharField(max_length=50, blank=True, null=True)
    on_trial = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.subscription} at {self.created_at}"
