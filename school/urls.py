from django.urls import path, include
from rest_framework.routers import DefaultRouter
from school.viewsets.admin_subscription_views import AdminSubscriptionHistoryViewSet, DashboardSummaryAPIView, RevenueActivityAPIView, SchoolOnboardingActivityAPIView, SubscriptionExpiringSoonAPIView
from school.viewsets.subscription_views import SubscriptionHistoryViewSet

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionHistoryViewSet, basename='subscription-history')
router.register(r'admin/schoolsubscription', AdminSubscriptionHistoryViewSet, basename='admin-schoolsubscription')

urlpatterns = [
    path('', include(router.urls)),
    path("dashboard/summary/",              DashboardSummaryAPIView.as_view(),           name="dashboard-summary"),
    path("dashboard/revenue-activity/",     RevenueActivityAPIView.as_view(),            name="revenue-activity"),
    path("dashboard/school-onboarding/",    SchoolOnboardingActivityAPIView.as_view(),   name="school-onboarding"),
    path("dashboard/expiring-soon/",        SubscriptionExpiringSoonAPIView.as_view(),   name="expiring-soon"),  
]
