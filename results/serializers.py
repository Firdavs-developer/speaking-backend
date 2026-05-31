from rest_framework import serializers

from .models import Answer, Result


class AnswerSerializer(serializers.ModelSerializer):
    durationSeconds = serializers.IntegerField(source="duration_seconds", required=False)

    class Meta:
        model = Answer
        fields = ["part", "question", "transcript", "durationSeconds"]


class ResultSerializer(serializers.ModelSerializer):
    """Read representation of a stored result."""

    answers = AnswerSerializer(many=True, read_only=True)
    overallBand = serializers.FloatField(source="overall_band", read_only=True)
    estimatedCefr = serializers.CharField(source="estimated_cefr", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Result
        fields = [
            "id",
            "overallBand",
            "estimatedCefr",
            "summary",
            "evaluation",
            "answers",
            "createdAt",
        ]


class AdminResultSerializer(serializers.ModelSerializer):
    """Result representation for admins — includes the student's identity."""

    answers = AnswerSerializer(many=True, read_only=True)
    overallBand = serializers.FloatField(source="overall_band", read_only=True)
    estimatedCefr = serializers.CharField(source="estimated_cefr", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    studentName = serializers.SerializerMethodField()
    studentEmail = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = [
            "id",
            "studentName",
            "studentEmail",
            "overallBand",
            "estimatedCefr",
            "summary",
            "evaluation",
            "answers",
            "createdAt",
        ]

    def get_studentName(self, obj):
        # Prefer the name typed before the test; fall back to the account name.
        if obj.student_name:
            return obj.student_name
        return obj.user.name if obj.user else "Anonymous"

    def get_studentEmail(self, obj):
        return obj.user.email if obj.user else ""


class CreateResultSerializer(serializers.Serializer):
    """Accepts { answers: [...], evaluation: {...}, studentName } from the frontend."""

    answers = serializers.ListField(child=serializers.DictField(), allow_empty=False)
    evaluation = serializers.DictField(required=False, default=dict)
    studentName = serializers.CharField(required=False, allow_blank=True, default="")

    def create(self, validated_data):
        evaluation = validated_data.get("evaluation") or {}
        user = self.context["request"].user
        user = user if user.is_authenticated else None

        overall_band = evaluation.get("overallBand")
        if not isinstance(overall_band, (int, float)):
            overall_band = None

        result = Result.objects.create(
            user=user,
            student_name=str(validated_data.get("studentName") or "")[:120],
            overall_band=overall_band,
            estimated_cefr=str(evaluation.get("estimatedCefr") or "")[:8],
            summary=str(evaluation.get("summary") or ""),
            evaluation=evaluation,
        )

        answers = []
        for index, raw in enumerate(validated_data["answers"]):
            duration = raw.get("durationSeconds", 0)
            answers.append(
                Answer(
                    result=result,
                    part=str(raw.get("part") or "")[:20],
                    question=str(raw.get("question") or ""),
                    transcript=str(raw.get("transcript") or ""),
                    duration_seconds=int(duration) if isinstance(duration, (int, float)) else 0,
                    order=index,
                )
            )
        Answer.objects.bulk_create(answers)

        return result
