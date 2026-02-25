from rest_framework.routers import DefaultRouter
from student.viewsets.studentattempts_views import StudentAttemptsViewSet
from student.viewsets.adminschoolviews import SchoolBasicViewSet
from student.viewsets.adminstudent_views import StudentViewSet
from student.viewsets.admintopstudent_views import TopStudentViewSet

router = DefaultRouter()
router.register(r'student-attempts', StudentAttemptsViewSet, basename='student-attempts')
router.register(r'school-list', SchoolBasicViewSet, basename='school-basic')
router.register(r'students-list', StudentViewSet, basename='student')
router.register(r'top-students',TopStudentViewSet,basename='topstudent')



urlpatterns = router.urls
