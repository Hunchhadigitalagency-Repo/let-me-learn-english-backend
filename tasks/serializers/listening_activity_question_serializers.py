from rest_framework import serializers
from tasks.models import ListeningActivityQuestion


# --------------------------
# Serializer for creating/updating a ListeningActivityQuestion
# --------------------------
class ListeningActivityQuestionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ListeningActivityQuestion
        fields = [
            'id',
            'listening_activity_part',   # ✅ corrected
            'question_type',             # ✅ corrected
            'question',
            'answer_1',
            'answer_2',
            'answer_3',
            'answer_4',
            'is_correct_answer'
        ]


# --------------------------
# Serializer for listing/retrieving a ListeningActivityQuestion
# --------------------------
from rest_framework import serializers
from tasks.models import ListeningActivityPart, ListeningActivityQuestion


# --------------------------
# Serializer for creating/updating a ListeningActivityQuestion
# --------------------------
class ListeningActivityQuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningActivityQuestion
        fields = [
            'id',
            'listening_activity_part',  # ✅ corrected
            'question_type',            # ✅ corrected
            'question',
            'answer_1',
            'answer_2',
            'answer_3',
            'answer_4',
            'is_correct_answer'
        ]


# --------------------------
# Serializer for listing/retrieving a ListeningActivityQuestion
# --------------------------
class ListeningActivityQuestionListSerializer(serializers.ModelSerializer):
    listening_activity_part = serializers.SerializerMethodField()

    class Meta:
        model = ListeningActivityQuestion
        fields = [
            'id',
            'listening_activity_part',  # ✅ corrected
            'question_type',            # ✅ corrected
            'question',
            'answer_1',
            'answer_2',
            'answer_3',
            'answer_4',
            'is_correct_answer'
        ]

    def get_listening_activity_part(self, obj):
        if obj.listening_activity_part:
            part = obj.listening_activity_part
            activity = part.listening_activity
            return {
                "part_id": part.id,
                "part_name": part.part,
                "listening_activity": {
                    "id": activity.id if activity else None,
                    "title": activity.title if activity else None,
                }
            }
        return None


# --------------------------
# Serializer for Creating ListeningActivityPart
# --------------------------
class ListeningActivityPartCreateSerializer(serializers.ModelSerializer):
    questions = ListeningActivityQuestionCreateSerializer(many=True)

    class Meta:
        model = ListeningActivityPart
        fields = [
            "id",
            "listening_activity",
            "part",
            "audio_file",
            "instruction",
            "questions",
        ]

    # --------------------------
    # Create Part + Nested Questions
    # --------------------------
    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])

        # Create the part
        part = ListeningActivityPart.objects.create(**validated_data)

        # Create nested questions
        question_instances = [
            ListeningActivityQuestion(listening_activity_part=part, **question_data)
            for question_data in questions_data
        ]
        ListeningActivityQuestion.objects.bulk_create(question_instances)

        return part

    # --------------------------
    # Update Part + Replace All Questions
    # --------------------------
    def update(self, instance, validated_data):
        questions_data = validated_data.pop("questions", [])

        # Update part fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Delete old questions
        instance.listeningactivityquestion_set.all().delete()

        # Create new questions
        question_instances = [
            ListeningActivityQuestion(listening_activity_part=instance, **question_data)
            for question_data in questions_data
        ]
        ListeningActivityQuestion.objects.bulk_create(question_instances)

        return instance