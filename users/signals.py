"""Signals für die ClubAuth users-App.

Wenn eine AppRoleAssignment für kursanmeldung oder vereinsheimbuchung gespeichert
oder gelöscht wird, wird der entsprechende User sofort per Webhook übermittelt.
"""

import logging
import requests
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import AppRoleAssignment

logger = logging.getLogger(__name__)

_KURSANMELDUNG_APP       = AppRoleAssignment.App.KURSANMELDUNG
_VEREINSHEIMBUCHUNG_APP  = AppRoleAssignment.App.VEREINSHEIMBUCHUNG


def _notify(webhook_url, user, role, action="upsert"):
    """Sendet eine Webhook-Anfrage an eine App."""
    import urllib.parse
    api_key = getattr(settings, "INTERNAL_API_KEY", "")
    if not webhook_url or not api_key:
        logger.warning("Webhook-URL oder INTERNAL_API_KEY fehlt – Sync übersprungen für %s", user.email)
        return
    # Host-Header aus der konfigurierten Webhook-URL ableiten, damit Django
    # ALLOWED_HOSTS nicht blockiert (relevant wenn interne IP/Port genutzt wird)
    parsed = urllib.parse.urlparse(webhook_url)
    host_header = parsed.hostname  # nur Hostname ohne Port
    payload = {
        "action":     action,
        "email":      user.email,
        "first_name": user.first_name,
        "last_name":  user.last_name,
        "role":       role,
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    if host_header:
        headers["Host"] = host_header
    try:
        resp = requests.post(
            f"{webhook_url.rstrip('/')}/api/sync-user/",
            json=payload,
            headers=headers,
            timeout=5,
        )
        resp.raise_for_status()
        logger.info("Sync OK (%s): %s (%s) action=%s", webhook_url, user.email, role, action)
    except requests.RequestException as exc:
        logger.error("Sync fehlgeschlagen (%s) für %s: %s", webhook_url, user.email, exc)


def _notify_kursanmeldung(user, role, action="upsert"):
    url = getattr(settings, "KURSANMELDUNG_WEBHOOK_URL", "")
    _notify(url, user, role, action)


def _notify_vereinsheimbuchung(user, role, action="upsert"):
    url = getattr(settings, "VEREINSHEIMBUCHUNG_WEBHOOK_URL", "")
    _notify(url, user, role, action)


@receiver(post_save, sender=AppRoleAssignment)
def on_role_assignment_saved(sender, instance, **kwargs):
    if instance.app == _KURSANMELDUNG_APP:
        _notify_kursanmeldung(instance.user, instance.role, action="upsert")
    elif instance.app == _VEREINSHEIMBUCHUNG_APP:
        _notify_vereinsheimbuchung(instance.user, instance.role, action="upsert")


@receiver(post_delete, sender=AppRoleAssignment)
def on_role_assignment_deleted(sender, instance, **kwargs):
    if instance.app == _KURSANMELDUNG_APP:
        _notify_kursanmeldung(instance.user, instance.role, action="remove")
    elif instance.app == _VEREINSHEIMBUCHUNG_APP:
        _notify_vereinsheimbuchung(instance.user, instance.role, action="remove")


@receiver(post_save, sender="users.CustomUser")
def on_user_saved(sender, instance, **kwargs):
    for assignment in AppRoleAssignment.objects.filter(user=instance):
        if assignment.app == _KURSANMELDUNG_APP:
            _notify_kursanmeldung(instance, assignment.role, action="upsert")
        elif assignment.app == _VEREINSHEIMBUCHUNG_APP:
            _notify_vereinsheimbuchung(instance, assignment.role, action="upsert")


@receiver(post_delete, sender="users.CustomUser")
def on_user_deleted(sender, instance, **kwargs):
    _notify_kursanmeldung(instance, "", action="delete")
    _notify_vereinsheimbuchung(instance, "", action="delete")
