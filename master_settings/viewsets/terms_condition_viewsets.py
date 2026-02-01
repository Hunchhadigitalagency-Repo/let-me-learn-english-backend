from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from master_settings.models import TermsandConditions
from master_settings.serializers.terms_condition_serializers import TermsandConditionsSerializer
from utils.permissions import IsAdminUserType
from utils.decorators import has_permission
class TermsandConditionsViewSet(ViewSet):
    """
    Singleton Terms and Conditions APIs
    """
    permission_classes = [IsAuthenticated]
    @has_permission("can_read_termscondition")
    @swagger_auto_schema(
        tags=['admin.terms-and-conditions'],
        operation_summary="Get Terms and Conditions",
        operation_description="Fetch the single terms and conditions configuration"
    )
    def list(self, request):
        """
        GET /terms-conditions/
        """
        policy = TermsandConditions.objects.first()
        if not policy:
            return Response({}, status=status.HTTP_200_OK)

        serializer = TermsandConditionsSerializer(policy)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @has_permission("can_write_termscondition")

    @swagger_auto_schema(
        tags=['admin.terms-and-conditions'],
        operation_summary="Create or Update Terms and Conditions",
        operation_description=(
            "Creates the terms and conditions if it does not exist, "
            "otherwise updates the existing single entry"
        ),
        request_body=TermsandConditionsSerializer
    )
    def create(self, request):
        """
        POST /terms-conditions/
        """
        policy = TermsandConditions.objects.first()

        serializer = TermsandConditionsSerializer(
            instance=policy,
            data=request.data,
            partial=True  # Allow partial updates
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK if policy else status.HTTP_201_CREATED
        )
