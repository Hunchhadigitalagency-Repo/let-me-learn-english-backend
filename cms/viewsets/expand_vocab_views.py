from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from cms.models import ExpandVocab

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from cms.serializers.expand_vocab_serializers import ExpandVocabSerializer
from utils.paginator import CustomPageNumberPagination


class ExpandVocabViewSet(ModelViewSet):
    """
    Admin Expand Vocab CRUD APIs
    """
    queryset = ExpandVocab.objects.all().order_by('word')
    serializer_class = ExpandVocabSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    # Search + Filter + Ordering
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # 🔍 Search by keyword
    search_fields = [
        'word'
    ]

    # 🎯 Filter by all possible fields
    filterset_fields = [
        'is_active',
        'used_status',
        'forced_publish',
        'grade',
        'created_at',
        'updated_at'
    ]

    ordering_fields = ['created_at', 'updated_at', 'word']

    # ---------- Swagger Overrides ----------

    @swagger_auto_schema(
        tags=['admin.expandvocab'],
        operation_summary="List Expand Vocabulary",
        operation_description="Paginated list of expand vocabulary with search and filters"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['admin.expandvocab'],
        operation_summary="Create Expand Vocabulary",
        operation_description="Create a new expand vocabulary entry"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['admin.expandvocab'],
        operation_summary="Retrieve Expand Vocabulary",
        operation_description="Retrieve a single expand vocabulary entry by ID"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['admin.expandvocab'],
        operation_summary="Update Expand Vocabulary",
        operation_description="Fully update an expand vocabulary entry"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['admin.expandvocab'],
        operation_summary="Partial Update Expand Vocabulary",
        operation_description="Partially update an expand vocabulary entry"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['admin.expandvocab'],
        operation_summary="Delete Expand Vocabulary",
        operation_description="Delete an expand vocabulary entry"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
