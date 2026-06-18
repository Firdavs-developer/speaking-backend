from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Validates registration data coming from the frontend register form."""

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "name", "email", "password"]

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Bu email allaqachon ro'yxatdan o'tgan."
            )
        return email

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data.get("name", "").strip(),
        )


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
