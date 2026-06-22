from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    MeView,
    PanelAdminDeleteView,
    PanelAdminListView,
    PanelAdminLoginView,
    PasswordResetConfirmView,
    PasswordResetRequestCodeView,
    PasswordResetVerifyCodeView,
    RegisterCompleteView,
    RegisterRequestCodeView,
    RegisterVerifyCodeView,
    SuperAdminLoginView,
    UserBlockView,
    UserDeleteView,
    UserUnblockView,
    UsersListView,
)

urlpatterns = [
    path(
        "register/request-code/",
        RegisterRequestCodeView.as_view(),
        name="register-request-code",
    ),
    path(
        "register/verify-code/",
        RegisterVerifyCodeView.as_view(),
        name="register-verify-code",
    ),
    path(
        "register/complete/",
        RegisterCompleteView.as_view(),
        name="register-complete",
    ),
    path(
        "password-reset/request-code/",
        PasswordResetRequestCodeView.as_view(),
        name="password-reset-request-code",
    ),
    path(
        "password-reset/verify-code/",
        PasswordResetVerifyCodeView.as_view(),
        name="password-reset-verify-code",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    # Panel admin accounts (managed by the super admin).
    path("admins/login/", PanelAdminLoginView.as_view(), name="panel-admin-login"),
    path(
        "admins/super-login/",
        SuperAdminLoginView.as_view(),
        name="super-admin-login",
    ),
    path("admins/", PanelAdminListView.as_view(), name="panel-admins"),
    path(
        "admins/<int:pk>/",
        PanelAdminDeleteView.as_view(),
        name="panel-admin-delete",
    ),
    path("users/", UsersListView.as_view(), name="users"),
    path("users/<int:pk>/block/", UserBlockView.as_view(), name="user-block"),
    path("users/<int:pk>/unblock/", UserUnblockView.as_view(), name="user-unblock"),
    path("users/<int:pk>/", UserDeleteView.as_view(), name="user-delete"),
]
