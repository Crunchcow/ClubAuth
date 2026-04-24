from django.contrib.auth import logout as auth_logout, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_GET
from django.contrib import messages
from .models import AppRoleAssignment
import hmac


# App-Namen → Hub-Kachel-Keys (müssen mit index.html data-app übereinstimmen)
_APP_TILE_MAP = {
    AppRoleAssignment.App.VEREINSHEIMBUCHUNG: "buchung",
    AppRoleAssignment.App.VEREINSHEIM:        "entnahmen",
    AppRoleAssignment.App.TENNISCOURTS:       "tennis",
    AppRoleAssignment.App.SPIELBETRIEB:       "spielbetrieb",
    AppRoleAssignment.App.KURSANMELDUNG:      "kurse",
}


class ClubAuthLoginView(LoginView):
    template_name = "registration/login.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ms_enabled"] = bool(
            getattr(settings, "SOCIAL_AUTH_MICROSOFT_OAUTH2_KEY", "")
        )
        ctx["error"] = self.request.GET.get("error")
        return ctx


@login_required
def profile_view(request):
    roles = AppRoleAssignment.objects.filter(user=request.user).order_by("app")
    return render(request, "users/profile.html", {"roles": roles})


@login_required
def force_password_change(request):
    """Erzwingt Passwort-Änderung wenn must_change_password gesetzt ist."""
    if not request.user.must_change_password:
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.must_change_password = False
            user.save(update_fields=["must_change_password"])
            update_session_auth_hash(request, user)
            messages.success(request, "Dein Passwort wurde erfolgreich gesetzt.")
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "registration/force_password_change.html", {"form": form})


class ClubAuthPasswordChangeView(PasswordChangeView):
    """Überschreibt die Standard-PasswordChangeView, um den must_change_password-Flag zurückzusetzen."""
    template_name = "registration/password_change_form.html"
    success_url = "/profile/"

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.user.must_change_password = False
        self.request.user.save(update_fields=["must_change_password"])
        return response


def hub_logout(request):
    """Logout per GET – für Hub-Verwendung (kein CSRF nötig)."""
    auth_logout(request)
    hub_origin = getattr(settings, "HUB_ORIGIN", "http://89.167.0.28:8088")
    return redirect(hub_origin)


@require_GET
def app_users(request):
    """Gibt alle User einer App mit ihren Rollen zurück.
    Gesichert via INTERNAL_API_KEY im Authorization-Header."""
    expected_key = getattr(settings, "INTERNAL_API_KEY", "")
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    token = auth_header.removeprefix("Bearer ").strip()

    if not expected_key or not hmac.compare_digest(token, expected_key):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    app = request.GET.get("app", "")
    if not app:
        return JsonResponse({"error": "Missing 'app' parameter"}, status=400)

    assignments = AppRoleAssignment.objects.filter(app=app).select_related("user")
    users = [
        {
            "email":      a.user.email,
            "first_name": a.user.first_name,
            "last_name":  a.user.last_name,
            "role":       a.role,
        }
        for a in assignments
    ]
    return JsonResponse({"users": users})


@require_GET
def hub_status(request):
    """Gibt den Login-Status und erlaubte Apps für den Hub zurück.
    CORS-Header erlauben den Aufruf vom Hub (anderer Port)."""
    hub_origin = getattr(settings, "HUB_ORIGIN", "http://89.167.0.28:8088")

    if not request.user.is_authenticated:
        response = JsonResponse({"authenticated": False})
        response["Access-Control-Allow-Origin"] = hub_origin
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    assignments = AppRoleAssignment.objects.filter(
        user=request.user
    ).values_list("app", flat=True)

    allowed_tiles = [
        _APP_TILE_MAP[app]
        for app in assignments
        if app in _APP_TILE_MAP
    ]
    # Admin bekommt Zugriff auf alle Tiles
    if request.user.is_staff:
        allowed_tiles = list(_APP_TILE_MAP.values())

    data = {
        "authenticated": True,
        "name": request.user.first_name or request.user.email.split("@")[0],
        "email": request.user.email,
        "is_admin": request.user.is_staff,
        "allowed_tiles": allowed_tiles,
    }
    response = JsonResponse(data)
    response["Access-Control-Allow-Origin"] = hub_origin
    response["Access-Control-Allow-Credentials"] = "true"
    return response
