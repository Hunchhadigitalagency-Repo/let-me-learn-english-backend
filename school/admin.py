from django.contrib import admin
from .models import Subscription, SubscriptionLog


# ------------------ Subscription Admin ------------------

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "school",
        "package",
        "subscription_type",
        "status",
        "payment_mode",
        "amount",
        "on_trial",
        "start_date",
        "end_date",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "payment_mode", "subscription_type", "on_trial")
    search_fields = ("school__name", "school__user__username", "package")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")


# ------------------ SubscriptionLog Admin ------------------

@admin.register(SubscriptionLog)
class SubscriptionLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subscription",
        "changed_by",
        "get_changed_keys",
        "remarks",
        "created_at",
    )
    list_filter = ("changed_by",)
    search_fields = (
        "subscription__school__name",
        "subscription__school__user__username",
        "changed_by__username",
        "remarks",
    )
    ordering = ("-created_at",)
    readonly_fields = ("subscription", "changed_by", "changed_fields", "remarks", "created_at")

    @admin.display(description="Changed Fields")
    def get_changed_keys(self, obj):
        """Shows which fields were changed, e.g. 'status, amount'"""
        if obj.changed_fields:
            return ", ".join(obj.changed_fields.keys())
        return "—"