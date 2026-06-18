from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
    UserBlockView,
    UserDeleteView,
    UserUnblockView,
    UsersListView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("users/", UsersListView.as_view(), name="users"),
    path("users/<int:pk>/block/", UserBlockView.as_view(), name="user-block"),
    path("users/<int:pk>/unblock/", UserUnblockView.as_view(), name="user-unblock"),
    path("users/<int:pk>/", UserDeleteView.as_view(), name="user-delete"),
]
