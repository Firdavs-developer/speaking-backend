import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Manager for the email-based custom user model."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """A registered speaking-app user, stored in the database."""

    name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.name or 'User'} <{self.email}>"


class PanelAdmin(models.Model):
    """An admin account created by the super admin to access the /admin panel.

    Admins log in with email + password. The password is stored in plaintext on
    purpose, so the super admin can read it back to an admin who forgets it.
    These are separate from `User` (app students) and from Django superusers.
    """

    name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.name or 'Admin'} <{self.email}>"


def generate_code():
    """A fresh 6-digit numeric verification code."""
    return f"{secrets.randbelow(1_000_000):06d}"


class EmailVerification(models.Model):
    """A one-time 6-digit code emailed to verify registration or reset a password.

    One active code is kept per (email, purpose); requesting a new one
    overwrites the old. Codes expire after CODE_TTL and lock after MAX_ATTEMPTS
    wrong tries.
    """

    PURPOSE_REGISTER = "register"
    PURPOSE_RESET = "reset"
    PURPOSE_CHOICES = [
        (PURPOSE_REGISTER, "register"),
        (PURPOSE_RESET, "reset"),
    ]

    CODE_TTL = timedelta(minutes=10)
    MAX_ATTEMPTS = 5

    email = models.EmailField()
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    code = models.CharField(max_length=6)
    # The display name captured at step 1 of registration (unused for resets).
    name = models.CharField(max_length=150, blank=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("email", "purpose")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.purpose} code for {self.email}"

    def is_expired(self):
        return timezone.now() > self.created_at + self.CODE_TTL
