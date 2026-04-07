import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="E-Mail")
    first_name = models.CharField(max_length=100, blank=True, verbose_name="Vorname")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Nachname")
    is_active = models.BooleanField(default=True, verbose_name="Aktiv")
    is_staff = models.BooleanField(default=False, verbose_name="Mitarbeiter")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Registriert")
    # Azure Entra ID Object-ID — wird beim Microsoft-Login automatisch befüllt
    microsoft_oid = models.CharField(
        max_length=200, blank=True, db_index=True, verbose_name="Microsoft OID"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = CustomUserManager()

    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def __str__(self) -> str:
        return f"{self.display_name} <{self.email}>"

    class Meta:
        verbose_name = "Benutzer"
        verbose_name_plural = "Benutzer"
        ordering = ["last_name", "first_name"]


class AppRoleAssignment(models.Model):
    """Weist einem Benutzer eine Rolle in einer bestimmten Vereinsanwendung zu."""

    class App(models.TextChoices):
        SPIELBETRIEB = "spielbetrieb", "Spielbetrieb"
        VEREINSHEIMBUCHUNG = "vereinsheimbuchung", "Vereinsheimbuchung"
        TENNISCOURTS = "tenniscourts", "Tenniscourts"
        VEREINSHEIM = "vereinsheim", "Vereinsheim"

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        KOORDINATOR = "koordinator", "Koordinator"     # Spielbetrieb
        BENUTZER = "benutzer", "Benutzer / Trainer"    # Spielbetrieb
        VERWALTUNG = "verwaltung", "Verwaltung"        # Vereinsheimbuchung
        VIEWER = "viewer", "Nur lesen"

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="role_assignments",
        verbose_name="Benutzer",
    )
    app = models.CharField(
        max_length=50, choices=App.choices, verbose_name="Anwendung"
    )
    role = models.CharField(
        max_length=50, choices=Role.choices, verbose_name="Rolle"
    )
    # Optionales Team-Feld — relevant für Spielbetrieb-Trainer (Rolle: benutzer)
    # Beispiele: "1. Herren", "U19", "Damen"
    team = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Mannschaft",
        help_text="Nur für Spielbetrieb-Trainer relevant. Exakt so schreiben wie in der Saisonplanung.",
    )
    granted_by = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="granted_roles",
        verbose_name="Vergeben von",
    )
    granted_at = models.DateTimeField(auto_now_add=True, verbose_name="Vergeben am")

    class Meta:
        unique_together = [("user", "app")]
        verbose_name = "Rollenzuweisung"
        verbose_name_plural = "Rollenzuweisungen"
        ordering = ["app", "user__last_name"]

    def __str__(self) -> str:
        return f"{self.user.display_name} → {self.get_app_display()} [{self.get_role_display()}]"
