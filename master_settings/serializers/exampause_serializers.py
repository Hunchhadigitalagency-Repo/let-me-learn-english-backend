from rest_framework import serializers
from master_settings.models import ExamPause

class ExamPauseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamPause
        fields = [
            'id',
            'school',
            'start_date',
            'end_date',
            'grade',
            'mark_all_grade',
            'is_active'
        ]


from user.serializers.school_serializers import SchoolBasicSerializer


class ExamPauseListSerializer(serializers.ModelSerializer):
    school = SchoolBasicSerializer(read_only=True)

    class Meta:
        model = ExamPause
        fields = [
            'id',
            'school',
            'start_date',
            'end_date',
            'grade',
            'mark_all_grade',
            'is_active'
        ]