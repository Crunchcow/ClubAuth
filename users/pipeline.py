"""Social-Auth Pipeline-Schritte für ClubAuth."""

from __future__ import annotations


def associate_by_email(backend, details, user=None, *args, **kwargs):
    """
    Verknüpft einen Microsoft-Login mit einem bestehenden ClubAuth-Account,
    wenn die E-Mail-Adresse übereinstimmt.
    """
    if user:
        return  # bereits verknüpft

    from users.models import CustomUser

    email = details.get("email")
    if email:
        try:
            existing = CustomUser.objects.get(email__iexact=email)
            return {"user": existing}
        except CustomUser.DoesNotExist:
            pass


def save_microsoft_oid(backend, user, response, *args, **kwargs):
    """
    Speichert die Azure-OID im CustomUser-Modell, sofern noch nicht gesetzt.
    Die OID ist die stabile, eindeutige Microsoft-ID des Nutzers.
    """
    if backend.name != "microsoft-oauth2":
        return

    oid = response.get("oid") or response.get("sub", "")
    if oid and not user.microsoft_oid:
        user.microsoft_oid = oid
        user.save(update_fields=["microsoft_oid"])
