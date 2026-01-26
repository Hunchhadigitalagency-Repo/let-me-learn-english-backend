from rest_framework import serializers
from tasks.models import (
    Task,
    SpeakingActivity, SpeakingActivityQuestion, speakingActivitySample,
    ReadingActivity, ReadingAcitivityQuestion,
    ListeningActivity, ListeningActivityQuestion,
    WritingActivity,
)


class IELTSListeningActivityQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningActivityQuestion
        fields = "__all__"


class IELTSListeningActivitySerializer(serializers.ModelSerializer):
    questions = IELTSListeningActivityQuestionSerializer(
        source="listeningactivityquestion_set", many=True, read_only=True
    )

    class Meta:
        model = ListeningActivity
        fields = "__all__"


class IELTSReadingQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingAcitivityQuestion
        fields = "__all__"


class IELTSReadingActivitySerializer(serializers.ModelSerializer):
    questions = IELTSReadingQuestionSerializer(
        source="readingacitivityquestion_set", many=True, read_only=True
    )

    class Meta:
        model = ReadingActivity
        fields = "__all__"


class IELTSWritingActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingActivity
        fields = "__all__"


class IELTSSpeakingQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeakingActivityQuestion
        fields = "__all__"


class IELTSSpeakingSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = speakingActivitySample
        fields = "__all__"


class IELTSSpeakingActivitySerializer(serializers.ModelSerializer):
    questions = IELTSSpeakingQuestionSerializer(
        source="speakingactivityquestion_set", many=True, read_only=True
    )
    samples = IELTSSpeakingSampleSerializer(
        source="speakingactivitysample_set", many=True, read_only=True
    )

    class Meta:
        model = SpeakingActivity
        fields = "__all__"


class IELTSTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
