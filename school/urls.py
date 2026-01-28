from django.urls import path, include
from rest_framework.routers import DefaultRouter
from school.viewsets.admin_subscription_views import AdminSubscriptionHistoryViewSet
from school.viewsets.subscription_views import SubscriptionHistoryViewSet

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionHistoryViewSet, basename='subscription-history')
router.register(r'admin/schoolsubscription', AdminSubscriptionHistoryViewSet, basename='admin-schoolsubscription')

urlpatterns = [
    path('', include(router.urls)),
]
