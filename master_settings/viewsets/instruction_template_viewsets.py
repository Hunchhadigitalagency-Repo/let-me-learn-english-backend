from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from master_settings.models import InstructionTemplate
from master_settings.serializers.instruction_template_serializers import InstructionTemplateSerializer

from utils.decorators import has_permission

class InstructionTemplateViewSet(ViewSet):
    """
    Singleton Instruction Template APIs
    """
    permission_classes = [IsAuthenticated]
    @has_permission("can_read_instructions")
    @swagger_auto_schema(
        tags=['admin.instructiontemplate'],
        operation_summary="Get Instruction Template",
        operation_description="Fetch the single instruction template configuration"
    )
    def list(self, request):
        instance = InstructionTemplate.objects.first()
        if not instance:
            return Response({}, status=status.HTTP_200_OK)

        serializer = InstructionTemplateSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    @has_permission("can_write_instructions")
    @swagger_auto_schema(
        tags=['admin.instructiontemplate'],
        operation_summary="Create or Update Instruction Template",
        operation_description=(
            "Creates the instruction template if not exists, "
            "otherwise updates the existing single entry"
        ),
        request_body=InstructionTemplateSerializer
    )
    def create(self, request):
        instance = InstructionTemplate.objects.first()

        serializer = InstructionTemplateSerializer(
            instance=instance,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK if instance else status.HTTP_201_CREATED
        )
