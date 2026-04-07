from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from .models import AppRoleAssignment


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
