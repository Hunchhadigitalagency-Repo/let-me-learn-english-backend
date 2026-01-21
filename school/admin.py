from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import SubscriptionHistory, SubscriptionLog

# ------------------ SubscriptionHistory Admin ------------------
@admin.register(SubscriptionHistory)
class SubscriptionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "school",
        "package",
        "status",
        "payment_mode",
        "amount",
        "start_date",
        "end_date",
        "created_at",
        "updated_at"
    )
    list_filter = ("status", "payment_mode", "school")
    search_fields = ("school__user__username", "package", "status")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

# ------------------ SubscriptionLog Admin ------------------
@admin.register(SubscriptionLog)
class SubscriptionLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subscription",
        "school",
        "changed_by",
        "old_status",
        "new_status",
        "old_amount",
        "new_amount",
        "old_payment_mode",
        "new_payment_mode",
        "created_at"
    )
    list_filter = ("school", "changed_by", "new_status", "new_payment_mode")
    search_fields = ("subscription__package", "school__user__username", "changed_by__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

