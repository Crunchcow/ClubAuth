from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.profile_view, name="home"),
    path("profile/", views.profile_view, name="profile"),
    path("accounts/login/", views.ClubAuthLoginView.as_view(), name="login"),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="/accounts/login/"),
        name="logout",
    ),
    path(
        "accounts/password-change/",
        auth_views.PasswordChangeView.as_view(success_url="/profile/"),
        name="password_change",
    ),
    path("api/hub-status/", views.hub_status, name="hub_status"),
    path("api/hub-logout/", views.hub_logout, name="hub_logout"),
]
