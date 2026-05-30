from rest_framework import serializers

from .models import Question


class QuestionSerializer(serializers.ModelSerializer):
    """Serializes a Question into the camelCase shape the frontend expects."""

    id = serializers.CharField(source="qid")
    partLabel = serializers.CharField(source="part_label", required=False)
    prepSeconds = serializers.IntegerField(source="prep_seconds", required=False)
    speakSeconds = serializers.IntegerField(source="speak_seconds", required=False)
    image = serializers.SerializerMethodField()
    cuePoints = serializers.ListField(
        source="cue_points", child=serializers.CharField(), required=False
    )

    class Meta:
        model = Question
        fields = [
            "id",
            "part",
            "partLabel",
            "question",
            "prepSeconds",
            "speakSeconds",
            "image",
            "cuePoints",
        ]

    def get_image(self, obj):
        if obj.image_src:
            return {"src": obj.image_src, "alt": obj.image_alt or "Question image"}
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Drop optional keys when empty so the payload matches the frontend type.
        if not data.get("image"):
            data.pop("image", None)
        if not data.get("cuePoints"):
            data.pop("cuePoints", None)
        return data


# Default timings per part (seconds), matching the frontend PART_DEFAULTS.
PART_DEFAULTS = {
    Question.PART_1: {"prep_seconds": 5, "speak_seconds": 30},
    Question.PART_2: {"prep_seconds": 60, "speak_seconds": 120},
    Question.PART_3: {"prep_seconds": 60, "speak_seconds": 120},
}


def _default_label(part):
    if part == Question.PART_2:
        return "Cue card"
    if part == Question.PART_3:
        return "Discussion"
    return "Question"


def normalize_question(raw, index=0):
    """Validate/normalize an arbitrary dict into Question field values, or None.

    Mirrors normalizeQuestion() in the frontend.
    """
    if not isinstance(raw, dict):
        return None

    part = raw.get("part")
    if part not in (Question.PART_1, Question.PART_2, Question.PART_3):
        return None

    question = (raw.get("question") or "").strip()
    if not question:
        return None

    qid = (raw.get("id") or "").strip()
    if not qid:
        slug = part.replace(" ", "").lower()
        qid = f"{slug}-{question[:8]}"

    fallback = PART_DEFAULTS[part]

    prep = raw.get("prepSeconds")
    prep_seconds = int(round(prep)) if isinstance(prep, (int, float)) and prep >= 0 else fallback["prep_seconds"]

    speak = raw.get("speakSeconds")
    speak_seconds = int(round(speak)) if isinstance(speak, (int, float)) and speak > 0 else fallback["speak_seconds"]

    values = {
        "qid": qid,
        "part": part,
        "part_label": (raw.get("partLabel") or "").strip() or _default_label(part),
        "question": question,
        "prep_seconds": prep_seconds,
        "speak_seconds": speak_seconds,
        "image_src": "",
        "image_alt": "",
        "cue_points": [],
        "order": index,
    }

    image = raw.get("image")
    if isinstance(image, dict):
        src = (image.get("src") or "").strip()
        if src:
            values["image_src"] = src
            values["image_alt"] = (image.get("alt") or "").strip() or "Question image"

    cue_points = raw.get("cuePoints")
    if isinstance(cue_points, list):
        cleaned = [str(p).strip() for p in cue_points if str(p).strip()]
        if cleaned:
            values["cue_points"] = cleaned

    return values
