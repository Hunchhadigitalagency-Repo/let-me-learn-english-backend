from rest_framework import serializers
from tasks.models import (
    Task,
    SpeakingActivity, SpeakingActivityQuestion, speakingActivitySample,
    ReadingActivity, ReadingAcitivityQuestion,
    ListeningActivity, ListeningActivityPart, ListeningActivityQuestion,
    WritingActivity,
)


# ==============================
# LISTENING
# ==============================

class IELTSListeningActivityQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningActivityQuestion
        fields = "__all__"


class IELTSListeningActivityPartSerializer(serializers.ModelSerializer):
    questions = IELTSListeningActivityQuestionSerializer(
        source="listeningactivityquestion_set",
        many=True,
        read_only=True
    )

    class Meta:
        model = ListeningActivityPart
        fields = "__all__"


class IELTSListeningActivitySerializer(serializers.ModelSerializer):
    parts = IELTSListeningActivityPartSerializer(
        source="listeningactivitypart_set",
        many=True,
        read_only=True
    )

    class Meta:
        model = ListeningActivity
        fields = "__all__"


# ==============================
# READING
# ==============================

class IELTSReadingQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingAcitivityQuestion
        fields = "__all__"


class IELTSReadingActivitySerializer(serializers.ModelSerializer):
    questions = IELTSReadingQuestionSerializer(
        source="readingacitivityquestion_set",
        many=True,
        read_only=True
    )

    class Meta:
        model = ReadingActivity
        fields = "__all__"


# ==============================
# WRITING
# ==============================

class IELTSWritingActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingActivity
        fields = "__all__"


# ==============================
# SPEAKING
# ==============================

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
        source="speakingactivityquestion_set",
        many=True,
        read_only=True
    )
    samples = IELTSSpeakingSampleSerializer(
        source="speakingactivitysample_set",
        many=True,
        read_only=True
    )

    class Meta:
        model = SpeakingActivity
        fields = "__all__"


# ==============================
# TASK
# ==============================

class IELTSTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"