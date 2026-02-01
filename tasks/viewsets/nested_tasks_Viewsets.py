from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from tasks.models import (
    Task, ListeningActivity, ReadingActivity, WritingActivity, SpeakingActivity
)
from tasks.serializers.nested_tasks_Serializers import (
    IELTSTaskSerializer,
    IELTSListeningActivitySerializer,
    IELTSReadingActivitySerializer,
    IELTSWritingActivitySerializer,
    IELTSSpeakingActivitySerializer,
)


class IELTSTaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Task.objects.all()
    serializer_class = IELTSTaskSerializer

    @action(detail=True, methods=["get"], url_path="")
    def modules(self, request, pk=None):
        module_type = request.query_params.get("type")
        if not module_type:
            raise ValidationError({
                "type": "This query param is required. e.g. ?type=listening"
            })

        task = self.get_object()
        module_type = module_type.lower()

        if module_type == "listening":
            qs = ListeningActivity.objects.filter(task=task)
            return Response(
                IELTSListeningActivitySerializer(qs, context={"request": request}, many=True).data
            )

        if module_type == "reading":
            qs = ReadingActivity.objects.filter(task=task)
            return Response(
                IELTSReadingActivitySerializer(qs, context={"request": request}, many=True).data
            )

        if module_type == "writing":
            qs = WritingActivity.objects.filter(task=task)
            return Response(
                IELTSWritingActivitySerializer(qs, context={"request": request}, many=True).data
            )

        if module_type == "speaking":
            qs = SpeakingActivity.objects.filter(task=task)
            return Response(
                IELTSSpeakingActivitySerializer(qs, context={"request": request}, many=True).data
            )

        if module_type == "all":
            return Response({
                "task": IELTSTaskSerializer(task, context={"request": request}).data,
                "listening": IELTSListeningActivitySerializer(
                    ListeningActivity.objects.filter(task=task), context={"request": request}, many=True
                ).data,
                "reading": IELTSReadingActivitySerializer(
                    ReadingActivity.objects.filter(task=task), context={"request": request}, many=True
                ).data,
                "writing": IELTSWritingActivitySerializer(
                    WritingActivity.objects.filter(task=task), context={"request": request}, many=True
                ).data,
                "speaking": IELTSSpeakingActivitySerializer(
                    SpeakingActivity.objects.filter(task=task), context={"request": request}, many=True
                ).data,
            })

        raise ValidationError({
            "type": "Invalid type. Use: listening, reading, writing, speaking, all"
        })
