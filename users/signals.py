"""Signals für die ClubAuth users-App.

Wenn eine AppRoleAssignment für kursanmeldung gespeichert oder gelöscht wird,
wird der entsprechende User sofort per Webhook an die Kursanmeldung übermittelt.
"""

import logging
import requests
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import AppRoleAssignment

logger = logging.getLogger(__name__)

_KURSANMELDUNG_APP = AppRoleAssignment.App.KURSANMELDUNG


def _notify_kursanmeldung(user, role, action="upsert"):
    """Sendet eine Webhook-Anfrage an die Kursanmeldung."""
    webhook_url = getattr(settings, "KURSANMELDUNG_WEBHOOK_URL", "").rstrip("/")
    api_key = getattr(settings, "INTERNAL_API_KEY", "")

    if not webhook_url or not api_key:
        logger.warning(
            "KURSANMELDUNG_WEBHOOK_URL oder INTERNAL_API_KEY nicht konfiguriert – "
            "Sync übersprungen für %s", user.email
        )
        return

    payload = {
        "action":     action,
        "email":      user.email,
        "first_name": user.first_name,
        "last_name":  user.last_name,
        "role":       role,
    }
    try:
        resp = requests.post(
            f"{webhook_url}/api/sync-user/",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5,
        )
        resp.raise_for_status()
        logger.info("Kursanmeldung-Sync OK: %s (%s) action=%s", user.email, role, action)
    except requests.RequestException as exc:
        logger.error("Kursanmeldung-Sync fehlgeschlagen für %s: %s", user.email, exc)


@receiver(post_save, sender=AppRoleAssignment)
def on_role_assignment_saved(sender, instance, **kwargs):
    if instance.app != _KURSANMELDUNG_APP:
        return
    _notify_kursanmeldung(instance.user, instance.role, action="upsert")


@receiver(post_delete, sender=AppRoleAssignment)
def on_role_assignment_deleted(sender, instance, **kwargs):
    if instance.app != _KURSANMELDUNG_APP:
        return
    _notify_kursanmeldung(instance.user, instance.role, action="remove")


@receiver(post_save, sender="users.CustomUser")
def on_user_saved(sender, instance, **kwargs):
    """Beim Speichern eines Users alle Kursanmeldung-Assignments synchronisieren.
    So wird der Sync auch ausgelöst wenn der Admin-Inline unverändert bleibt."""
    for assignment in AppRoleAssignment.objects.filter(
        user=instance, app=_KURSANMELDUNG_APP
    ):
        _notify_kursanmeldung(instance, assignment.role, action="upsert")


@receiver(post_delete, sender="users.CustomUser")
def on_user_deleted(sender, instance, **kwargs):
    """Wenn ein ClubAuth-User gelöscht wird, wird er auch aus der Kursanmeldung entfernt."""
    _notify_kursanmeldung(instance, "", action="delete")
