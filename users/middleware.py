from django.conf import settings
from django.shortcuts import redirect


_EXEMPT_PATHS = {
    "/accounts/login/",
    "/accounts/logout/",
    "/accounts/password-change/",
    "/accounts/password-reset/",
    "/accounts/password-reset/done/",
    "/accounts/password-change/done/",
    "/accounts/force-password-change/",
}


class ForcePasswordChangeMiddleware:
    """
    Leitet eingeloggte User mit must_change_password=True auf die
    Erzwinge-Passwort-Änderungsseite um, bevor sie irgendeine andere Seite besuchen.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and getattr(request.user, "must_change_password", False)
            and not request.path.startswith("/admin/")
            and not request.path.startswith("/static/")
            and not any(request.path.startswith(p) for p in _EXEMPT_PATHS)
        ):
            return redirect("/accounts/force-password-change/")

        return self.get_response(request)
