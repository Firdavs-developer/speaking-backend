from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Question
from .serializers import QuestionSerializer, normalize_question


def _is_admin(request):
    """The admin password doubles as the bearer token for question edits."""
    token = (request.headers.get("X-Admin-Token") or "").strip()
    return bool(token) and token == settings.ADMIN_PASSWORD


def _sorted_questions():
    qs = list(Question.objects.all())
    qs.sort(key=lambda q: (q.part_rank, q.order, q.id))
    return qs


class QuestionListView(APIView):
    """GET list of questions; POST (admin) replaces the whole question set."""

    permission_classes = [AllowAny]

    def get(self, request):
        questions = QuestionSerializer(_sorted_questions(), many=True).data
        return Response({"questions": questions})

    def post(self, request):
        if not _is_admin(request):
            return Response(
                {"error": "Ruxsat yo'q. Admin sifatida kiring."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        raw_questions = request.data.get("questions")
        if not isinstance(raw_questions, list):
            return Response(
                {"error": "Savollar noto'g'ri formatda yuborildi."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        normalized = []
        seen_qids = set()
        for index, raw in enumerate(raw_questions):
            values = normalize_question(raw, index)
            if values is None:
                continue
            # Avoid unique-constraint clashes on duplicate ids in one payload.
            if values["qid"] in seen_qids:
                values["qid"] = f"{values['qid']}-{index}"
            seen_qids.add(values["qid"])
            normalized.append(values)

        if not normalized:
            return Response(
                {"error": "Kamida bitta to'g'ri savol kerak."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            Question.objects.all().delete()
            Question.objects.bulk_create([Question(**values) for values in normalized])

        questions = QuestionSerializer(_sorted_questions(), many=True).data
        return Response({"questions": questions})
