from django.db import models
from django.contrib.auth import get_user_model
from user.models import School

User = get_user_model()


class Subscription(models.Model):
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
    SUBSCRIPTION_TYPE_CHOICES = (
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
        ("custom", "Custom"),
    )

    school = models.OneToOneField(
        School,
        on_delete=models.CASCADE,
        related_name="subscription"
    )
    package = models.CharField(max_length=255)
    subscription_type = models.CharField(
        max_length=50,
        choices=SUBSCRIPTION_TYPE_CHOICES,
        default="monthly"
    )
    amount = models.PositiveIntegerField()
    payment_mode = models.CharField(
        max_length=50,
        choices=PAYMENT_MODE_CHOICES
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="pending"
    )
    on_trial = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.school} - {self.package} ({self.subscription_type} / {self.status})"

    def snapshot(self):
        """Captures the current state of all tracked fields."""
        return {
            "package": self.package,
            "subscription_type": self.subscription_type,
            "amount": self.amount,
            "payment_mode": self.payment_mode,
            "status": self.status,
            "on_trial": self.on_trial,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date),
            "remarks": self.remarks,
        }

    def update_subscription(self, changed_by=None, remarks=None, **kwargs):
        """
        Single entry point for all updates.
        Always logs before/after — never call .save() directly.
        """
        before = self.snapshot()

        for field, value in kwargs.items():
            setattr(self, field, value)

        if remarks:
            self.remarks = remarks

        self.save()

        after = self.snapshot()

        # Only store fields that actually changed
        changed_fields = {
            key: {"old": before[key], "new": after[key]}
            for key in before
            if before[key] != after[key]
        }

        SubscriptionLog.objects.create(
            subscription=self,
            changed_by=changed_by,
            changed_fields=changed_fields,
            remarks=remarks,
        )


class SubscriptionLog(models.Model):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="logs"
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The user who made the change"
    )
    changed_fields = models.JSONField(
        default=dict,
        help_text="Stores only changed fields with old and new values"
    )
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Log #{self.pk} for {self.subscription} at {self.created_at}"