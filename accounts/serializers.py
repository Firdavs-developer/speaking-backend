from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import PanelAdmin, User


class LoginSerializer(serializers.Serializer):
    """Validates login credentials."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=attrs["password"],
        )
        if not user:
            # authenticate() rejects inactive users, so a correct password on a
            # blacklisted account lands here. Tell them they're blocked instead
            # of the generic "wrong credentials" message.
            blocked = User.objects.filter(email=email, is_active=False).first()
            if blocked and blocked.check_password(attrs["password"]):
                raise serializers.ValidationError(
                    "Siz administrator tomonidan bloklangansiz. "
                    "Blokdan chiqarish uchun adminga murojaat qiling."
                )
            raise serializers.ValidationError(
                "Email yoki parol noto'g'ri."
            )
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Public representation of a user (no password)."""

    class Meta:
        model = User
        fields = ["id", "name", "email", "date_joined"]


class AdminUserSerializer(serializers.ModelSerializer):
    """Admin view of a registered user, with how many tests they've taken."""

    results_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "email", "date_joined", "is_active", "results_count"]


class PanelAdminSerializer(serializers.ModelSerializer):
    """Super-admin view of a panel admin, including the plaintext password."""

    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = PanelAdmin
        fields = ["id", "name", "email", "password", "createdAt"]
