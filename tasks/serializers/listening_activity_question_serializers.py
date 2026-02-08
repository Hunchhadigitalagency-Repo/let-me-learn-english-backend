from rest_framework import serializers
from tasks.models import ListeningActivityQuestion
import json

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
    questions = ListeningActivityQuestionCreateSerializer(many=True, required=False)  # <-- here

    class Meta:
        model = ListeningActivityPart
        fields = [
            "id",
            "listening_activity",
            "part",
            "audio_file",
            "instruction",
            "duration",
            "questions",
        ]

    def to_internal_value(self, data):
        # Parse JSON string for `questions` if it's a string
        questions = data.get('questions')
        if isinstance(questions, str):
            try:
                data['questions'] = json.loads(questions)
            except json.JSONDecodeError:
                data['questions'] = []
        return super().to_internal_value(data)

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

        # Track IDs of questions from payload
        sent_question_ids = []

        for question_data in questions_data:
            question_id = question_data.get('id', None)

            if question_id:
                # Update existing question
                try:
                    question_instance = ListeningActivityQuestion.objects.get(
                        id=question_id,
                        listening_activity_part=instance
                    )
                    for attr, value in question_data.items():
                        if attr != 'id':
                            setattr(question_instance, attr, value)
                    question_instance.save()
                    sent_question_ids.append(question_instance.id)
                except ListeningActivityQuestion.DoesNotExist:
                    # If id does not exist, create new
                    new_question = ListeningActivityQuestion.objects.create(
                        listening_activity_part=instance, **question_data
                    )
                    sent_question_ids.append(new_question.id)
            else:
                # Create new question
                new_question = ListeningActivityQuestion.objects.create(
                    listening_activity_part=instance, **question_data
                )
                sent_question_ids.append(new_question.id)

        # # Optional: Delete questions not in payload
        # instance.listeningactivityquestion_set.exclude(id__in=sent_question_ids).delete()

        return instance