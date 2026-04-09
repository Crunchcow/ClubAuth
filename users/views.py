from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_GET
from .models import AppRoleAssignment


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
