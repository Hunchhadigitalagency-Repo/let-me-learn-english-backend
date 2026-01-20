from django.urls import path, include
from rest_framework.routers import DefaultRouter
from school.viewsets.subscription_views import SubscriptionHistoryViewSet

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionHistoryViewSet, basename='subscription-history')

urlpatterns = [
    path('', include(router.urls)),
]
