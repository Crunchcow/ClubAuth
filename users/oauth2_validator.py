from oauth2_provider.oauth2_validators import OAuth2Validator
from .models import AppRoleAssignment


class CustomOAuth2Validator(OAuth2Validator):
    """Erweitert den OIDC-Token um app-spezifische Rollen."""

    def get_userinfo_claims(self, request):
        claims = super().get_userinfo_claims(request)

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return claims

        # Anzeigename
        claims["name"] = user.display_name

        # Alle Rollenzuweisungen als Dict: { "spielbetrieb": "koordinator", ... }
        roles = {
            a["app"]: a["role"]
            for a in AppRoleAssignment.objects.filter(user=user).values("app", "role")
        }
        if roles:
            claims["roles"] = roles

        return claims
