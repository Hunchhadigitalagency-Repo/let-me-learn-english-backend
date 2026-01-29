from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from master_settings.models import PrivacyPolicy
from master_settings.serializers.privacy_policy_serializers import PrivacyPolicySerializer
from utils.permissions.admins.admin_perms_mixins import IsAdminUserType

class PrivacyPolicyViewSet(ViewSet):
   
    permission_classes = [IsAdminUserType]

    @swagger_auto_schema(
        tags=['admin.privacy-policy'],
        operation_summary="Get Privacy Policy",
        operation_description="Fetch the single privacy policy configuration"
    )
    def list(self, request):
      
        policy = PrivacyPolicy.objects.first()
        if not policy:
            return Response({}, status=status.HTTP_200_OK)

        serializer = PrivacyPolicySerializer(policy)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['admin.privacy-policy'],
        operation_summary="Create or Update Privacy Policy",
        operation_description=(
            "Creates the privacy policy if it does not exist, "
            "otherwise updates the existing single entry"
        ),
        request_body=PrivacyPolicySerializer
    )
    def create(self, request):
        """
        POST /privacy-policy/
        """
        policy = PrivacyPolicy.objects.first()

        serializer = PrivacyPolicySerializer(
            instance=policy,
            data=request.data,
            partial=True  
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK if policy else status.HTTP_201_CREATED
        )
