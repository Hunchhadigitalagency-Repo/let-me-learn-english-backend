from rest_framework.routers import DefaultRouter
from student.viewsets.studentattempts_views import StudentAttemptsViewSet
router = DefaultRouter()
router.register(r'student-attempts', StudentAttemptsViewSet, basename='student-attempts')


urlpatterns = router.urls
