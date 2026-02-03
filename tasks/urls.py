from django.urls import path, include
from rest_framework.routers import DefaultRouter

from tasks.viewsets.nested_tasks_Viewsets import IELTSTaskViewSet
from tasks.viewsets.speaking_activity_views import SpeakingActivityViewSet
from tasks.viewsets.tasks_views import TaskViewSet
from tasks.viewsets.speaking_activity_sample_views import SpeakingActivitySampleViewSet
from tasks.viewsets.speaking_activity_question_views import SpeakingActivityQuestionViewSet
from tasks.viewsets.reading_activity_views import ReadingActivityViewSet,ReadingActivityDropdownViewSet
from tasks.viewsets.reading_activity_question_views import ReadingActivityQuestionViewSet
from tasks.viewsets.listening_activity_views import ListeningActivityViewSet
from tasks.viewsets.listening_activity_question_views import ListeningActivityQuestionViewSet
from tasks.viewsets.writing_activity_views import WritingActivityViewSet
from tasks.viewsets.speaking_activity_views import SpeakingActivityDropdownViewSet
# Create the router
router = DefaultRouter()

# Register all your viewsets with the router
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'speaking-activities', SpeakingActivityViewSet, basename='speaking-activities')
router.register(r'speaking-activity-samples', SpeakingActivitySampleViewSet, basename='speaking-activity-samples')
router.register(r'speaking-activity-questions', SpeakingActivityQuestionViewSet, basename='speaking-activity-questions')
router.register(r'reading-activities', ReadingActivityViewSet, basename='reading-activities')
router.register(r'reading-activity-questions', ReadingActivityQuestionViewSet, basename='reading-activity-questions')
router.register(r'listening-activities', ListeningActivityViewSet, basename='listening-activities')
router.register(r'listening-activity-questions', ListeningActivityQuestionViewSet, basename='listening-activity-questions')
router.register(r'writing-activities', WritingActivityViewSet, basename='writing-activities')
router.register(r'nested-tasks', IELTSTaskViewSet, basename='nested-tasks')
router.register(r'speaking-activity-dropdown', SpeakingActivityDropdownViewSet, basename='speaking-activity-dropdown')
router.register(r'reading-activity-dropdown',ReadingActivityDropdownViewSet,basename='reading-activity-dropdown')


# Use router.urls in urlpatterns
urlpatterns = [
    path('', include(router.urls)), 
]
