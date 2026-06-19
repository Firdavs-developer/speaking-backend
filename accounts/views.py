from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmailVerification, User, generate_code
from .serializers import (
    AdminUserSerializer,
    LoginSerializer,
    UserSerializer,
)


def _is_admin(request):
    """The admin password doubles as the bearer token for admin views."""
    token = (request.headers.get("X-Admin-Token") or "").strip()
    return bool(token) and token == settings.ADMIN_PASSWORD


def _send_code_email(email, code, purpose):
    """Email a verification code as a styled HTML message (plain-text fallback).

    Subject/wording depend on whether it's for registration or a reset.
    """
    if purpose == EmailVerification.PURPOSE_RESET:
        subject = "Parolni tiklash kodi"
        title = "Parolni tiklash"
        action = "parolingizni tiklash"
    else:
        subject = "Ro'yxatdan o'tish kodi"
        title = "Ro'yxatdan o'tish"
        action = "ro'yxatdan o'tishni yakunlash"

    text_message = (
        f"Speaking Practice ilovasida {action} uchun tasdiqlash kodingiz:\n\n"
        f"    {code}\n\n"
        "Kod 10 daqiqa davomida amal qiladi. Agar bu siz bo'lmasangiz, "
        "ushbu xabarni e'tiborsiz qoldiring."
    )

    html_message = f"""\
<!DOCTYPE html>
<html lang="uz">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#f6f7f5;font-family:Arial,Helvetica,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f6f7f5;padding:32px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:480px;background-color:#ffffff;border:1px solid #e4e4e7;border-radius:14px;overflow:hidden;">
          <tr>
            <td style="padding:28px 32px 8px 32px;text-align:center;">
              <span style="display:inline-block;font-size:11px;font-weight:bold;letter-spacing:3px;color:#0f766e;text-transform:uppercase;">IELTS</span>
              <div style="font-size:20px;font-weight:bold;color:#18181b;margin-top:2px;">Speaking Practice</div>
            </td>
          </tr>
          <tr>
            <td style="padding:8px 32px 0 32px;text-align:center;">
              <h1 style="font-size:22px;color:#18181b;margin:16px 0 6px 0;">{title}</h1>
              <p style="font-size:14px;color:#71717a;line-height:1.6;margin:0;">
                {action.capitalize()} uchun quyidagi tasdiqlash kodini kiriting.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 32px;">
              <div style="background-color:#f0fdfa;border:1px solid #99f6e4;border-radius:12px;padding:18px;text-align:center;">
                <div style="font-size:36px;font-weight:bold;letter-spacing:10px;color:#0f766e;font-family:'Courier New',monospace;">{code}</div>
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:0 32px 8px 32px;text-align:center;">
              <p style="font-size:13px;color:#71717a;line-height:1.6;margin:0;">
                Kod <strong>10 daqiqa</strong> davomida amal qiladi.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:16px 32px 28px 32px;">
              <hr style="border:none;border-top:1px solid #f4f4f5;margin:0 0 16px 0;">
              <p style="font-size:12px;color:#a1a1aa;line-height:1.6;margin:0;text-align:center;">
                Agar bu siz bo'lmasangiz, ushbu xabarni e'tiborsiz qoldiring.
              </p>
            </td>
          </tr>
        </table>
        <p style="font-size:11px;color:#a1a1aa;margin:16px 0 0 0;">© Speaking Practice</p>
      </td>
    </tr>
  </table>
</body>
</html>"""

    send_mail(
        subject,
        text_message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=html_message,
        fail_silently=False,
    )


def _check_code(email, purpose, code):
    """Validate a submitted code against the stored one.

    Returns (verification, error_response). On success error_response is None
    and the matching row is returned; otherwise verification is None and a
    ready-to-return DRF Response describes the problem.
    """
    code = (code or "").strip()
    try:
        verification = EmailVerification.objects.get(email=email, purpose=purpose)
    except EmailVerification.DoesNotExist:
        return None, Response(
            {"error": "Kod topilmadi. Iltimos, qaytadan kod so'rang."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if verification.is_expired():
        verification.delete()
        return None, Response(
            {"error": "Kod muddati tugagan. Iltimos, qaytadan kod so'rang."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if verification.attempts >= EmailVerification.MAX_ATTEMPTS:
        verification.delete()
        return None, Response(
            {"error": "Juda ko'p urinish. Iltimos, qaytadan kod so'rang."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if verification.code != code:
        verification.attempts += 1
        verification.save(update_fields=["attempts"])
        return None, Response(
            {"error": "Kod noto'g'ri."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return verification, None


class RegisterRequestCodeView(APIView):
    """POST /api/auth/register/request-code/ — email a 6-digit code to start signup.

    Body: {name, email}. Fails if the email is already registered.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        name = (request.data.get("name") or "").strip()
        email = (request.data.get("email") or "").strip().lower()

        if not email:
            return Response(
                {"error": "Email kiritilishi shart."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Bu email allaqachon ro'yxatdan o'tgan."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        code = generate_code()
        EmailVerification.objects.update_or_create(
            email=email,
            purpose=EmailVerification.PURPOSE_REGISTER,
            defaults={
                "code": code,
                "name": name,
                "is_verified": False,
                "attempts": 0,
                "created_at": timezone.now(),
            },
        )
        _send_code_email(email, code, EmailVerification.PURPOSE_REGISTER)
        return Response({"ok": True})


class RegisterVerifyCodeView(APIView):
    """POST /api/auth/register/verify-code/ — confirm the emailed code is correct.

    Body: {email, code}. Marks the code verified but does not yet create a user.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        verification, error = _check_code(
            email, EmailVerification.PURPOSE_REGISTER, request.data.get("code")
        )
        if error:
            return error

        verification.is_verified = True
        verification.save(update_fields=["is_verified", "attempts"])
        return Response({"ok": True})


class RegisterCompleteView(APIView):
    """POST /api/auth/register/complete/ — set a password and create the account.

    Body: {email, code, password}. The code is re-checked, then the user is
    created with the password they chose and an auth token is returned.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password") or ""

        if len(password) < 6:
            return Response(
                {"error": "Parol kamida 6 ta belgidan iborat bo'lishi kerak."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        verification, error = _check_code(
            email, EmailVerification.PURPOSE_REGISTER, request.data.get("code")
        )
        if error:
            return error

        if User.objects.filter(email=email).exists():
            verification.delete()
            return Response(
                {"error": "Bu email allaqachon ro'yxatdan o'tgan."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            email=email,
            password=password,
            name=verification.name,
        )
        verification.delete()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class PasswordResetRequestCodeView(APIView):
    """POST /api/auth/password-reset/request-code/ — email a reset code.

    Body: {email}. Always reports success so registered emails aren't leaked;
    a code is only actually sent when the account exists and is active.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()

        user = User.objects.filter(email=email).first()
        if user and user.is_active:
            code = generate_code()
            EmailVerification.objects.update_or_create(
                email=email,
                purpose=EmailVerification.PURPOSE_RESET,
                defaults={
                    "code": code,
                    "name": "",
                    "is_verified": False,
                    "attempts": 0,
                    "created_at": timezone.now(),
                },
            )
            _send_code_email(email, code, EmailVerification.PURPOSE_RESET)

        return Response({"ok": True})


class PasswordResetVerifyCodeView(APIView):
    """POST /api/auth/password-reset/verify-code/ — confirm the reset code.

    Body: {email, code}.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        verification, error = _check_code(
            email, EmailVerification.PURPOSE_RESET, request.data.get("code")
        )
        if error:
            return error

        verification.is_verified = True
        verification.save(update_fields=["is_verified", "attempts"])
        return Response({"ok": True})


class PasswordResetConfirmView(APIView):
    """POST /api/auth/password-reset/confirm/ — set a new password.

    Body: {email, code, password}. Re-checks the code, updates the password and
    invalidates existing sessions.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password") or ""

        if len(password) < 6:
            return Response(
                {"error": "Parol kamida 6 ta belgidan iborat bo'lishi kerak."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        verification, error = _check_code(
            email, EmailVerification.PURPOSE_RESET, request.data.get("code")
        )
        if error:
            return error

        user = User.objects.filter(email=email).first()
        if not user:
            verification.delete()
            return Response(
                {"error": "Foydalanuvchi topilmadi."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save(update_fields=["password"])
        verification.delete()
        # Force a fresh login everywhere with the new password.
        Token.objects.filter(user=user).delete()
        return Response({"ok": True})


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


class UserBlockView(APIView):
    """POST /api/auth/users/<pk>/block/ — blacklist a user (admin only)."""

    permission_classes = [AllowAny]

    def post(self, request, pk):
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
                {"error": "Administratorni bloklab bo'lmaydi."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = False
        user.save(update_fields=["is_active"])
        # Kill any existing sessions so the block takes effect immediately.
        Token.objects.filter(user=user).delete()
        return Response({"ok": True})


class UserUnblockView(APIView):
    """POST /api/auth/users/<pk>/unblock/ — remove a user from the blacklist (admin only)."""

    permission_classes = [AllowAny]

    def post(self, request, pk):
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
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response({"ok": True})


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
