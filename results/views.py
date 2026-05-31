from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Result
from .serializers import (
    AdminResultSerializer,
    CreateResultSerializer,
    ResultSerializer,
)


def _is_admin(request):
    """The admin password doubles as the bearer token for admin views."""
    token = (request.headers.get("X-Admin-Token") or "").strip()
    return bool(token) and token == settings.ADMIN_PASSWORD


class ResultListCreateView(APIView):
    """POST a new result (auth optional); GET the current user's results."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        results = Result.objects.filter(user=request.user).prefetch_related("answers")
        return Response(ResultSerializer(results, many=True).data)

    def post(self, request):
        serializer = CreateResultSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(
            ResultSerializer(result).data, status=status.HTTP_201_CREATED
        )


class AllResultsView(APIView):
    """GET every student's result (admin only)."""

    permission_classes = [AllowAny]

    def get(self, request):
        if not _is_admin(request):
            return Response(
                {"error": "Ruxsat yo'q. Admin sifatida kiring."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        results = (
            Result.objects.select_related("user")
            .prefetch_related("answers")
            .order_by("-created_at")
        )
        return Response({"results": AdminResultSerializer(results, many=True).data})


class ResultDetailView(APIView):
    """GET a single result belonging to the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            result = Result.objects.prefetch_related("answers").get(pk=pk, user=request.user)
        except Result.DoesNotExist:
            return Response(
                {"error": "Natija topilmadi."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(ResultSerializer(result).data)
