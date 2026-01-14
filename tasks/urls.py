from django.urls import path
from tasks.viewsets.activity_views import SpeakingActivityViewSet
from tasks.viewsets.tasks_views import TaskViewSet
from tasks.viewsets.activity_sample_views import SpeakingActivitySampleViewSet

from tasks.viewsets.activity_question_views import SpeakingActivityQuestionViewSet
from tasks.viewsets.reading_activity_views import ReadingActivityViewSet
from tasks.viewsets.reading_activity_question_views import ReadingActivityQuestionViewSet
urlpatterns = [
    path('tasks/', TaskViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='task-list-create'),

    
    path('tasks/<int:pk>/', TaskViewSet.as_view({
        'get': 'retrieve',
       
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='task-detail'),
    path('speaking-activities/', SpeakingActivityViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='activity-list-create'),

    
    path('speaking-activities/<int:pk>/', SpeakingActivityViewSet.as_view({
        'get': 'retrieve',
       
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='activity-detail'),
    path('speaking-activity-samples/', SpeakingActivitySampleViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='sample-list-create'),

    path('speaking-activity-samples/<int:pk>/', SpeakingActivitySampleViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='sample-detail'),
    path('speaking-activity-questions/', SpeakingActivityQuestionViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='question-list-create'),

    path('speaking-activity-questions/<int:pk>/', SpeakingActivityQuestionViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='question-detail'),
    path('reading-activities/', ReadingActivityViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='reading-activity-list-create'),

    path('reading-activities/<int:pk>/', ReadingActivityViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='reading-activity-detail'),
    path('reading-activity-questions/', ReadingActivityQuestionViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='reading-question-list-create'),

    # Retrieve, update (PUT), partial update (PATCH), and delete
    path('reading-activity-questions/<int:pk>/', ReadingActivityQuestionViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='reading-question-detail'),
    
]
