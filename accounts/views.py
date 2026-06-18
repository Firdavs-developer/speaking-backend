from django.conf import settings
from django.db.models import Count
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import (
    AdminUserSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)


def _is_admin(request):
    """The admin password doubles as the bearer token for admin views."""
    token = (request.headers.get("X-Admin-Token") or "").strip()
    return bool(token) and token == settings.ADMIN_PASSWORD


class RegisterView(APIView):
    """POST /api/auth/register/ — create a user and return an auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /api/auth/login/ — authenticate and return an auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class MeView(APIView):
    """GET /api/auth/me/ — return the currently authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    """POST /api/auth/logout/ — invalidate the current auth token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsersListView(APIView):
    """GET /api/auth/users/ — every registered user (admin only)."""

    permission_classes = [AllowAny]

    def get(self, request):
        if not _is_admin(request):
            return Response(
                {"error": "Ruxsat yo'q. Admin sifatida kiring."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        users = User.objects.annotate(results_count=Count("results")).order_by(
            "-date_joined"
        )
        return Response({"users": AdminUserSerializer(users, many=True).data})


class UserDeleteView(APIView):
    """DELETE /api/auth/users/<pk>/ — permanently delete a user (admin only).

    Cascades to the user's auth token and saved results, leaving no trace.
    """

    permission_classes = [AllowAny]

    def delete(self, request, pk):
        if not _is_admin(request):
            return Response(
                {"error": "Ruxsat yo'q. Admin sifatida kiring."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "Foydalanuvchi topilmadi."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if user.is_superuser:
            return Response(
                {"error": "Administratorni o'chirib bo'lmaydi."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
