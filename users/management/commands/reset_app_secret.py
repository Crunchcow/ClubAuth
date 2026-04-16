"""
Management-Command: reset_app_secret

Generiert ein neues Client-Secret für eine OAuth2-Application in ClubAuth,
speichert es (ggf. gehasht) und gibt das Klartext-Secret einmalig aus.

Verwendung:
    python manage.py reset_app_secret --name Spielbetrieb
    python manage.py reset_app_secret --client-id pwCZWopkYJIEX30yfU8Y5Q4ie7ZmozsY3AXfv
"""

import secrets

from django.core.management.base import BaseCommand, CommandError
from oauth2_provider.models import Application


class Command(BaseCommand):
    help = "Setzt das Client-Secret einer OAuth2-Application zurück und gibt es einmalig als Klartext aus."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--name", help="Name der Application (z. B. 'Spielbetrieb')")
        group.add_argument("--client-id", help="Client-ID der Application")

    def handle(self, *args, **options):
        if options["name"]:
            try:
                app = Application.objects.get(name=options["name"])
            except Application.DoesNotExist:
                raise CommandError(f"Keine Application mit dem Namen '{options['name']}' gefunden.")
        else:
            try:
                app = Application.objects.get(client_id=options["client_id"])
            except Application.DoesNotExist:
                raise CommandError(f"Keine Application mit der Client-ID '{options['client_id']}' gefunden.")

        new_secret = secrets.token_urlsafe(40)
        app.client_secret = new_secret
        app.save()

        self.stdout.write(self.style.SUCCESS(f"\n✅ Secret für '{app.name}' erfolgreich zurückgesetzt.\n"))
        self.stdout.write(self.style.WARNING("=" * 60))
        self.stdout.write(self.style.WARNING(f"  Client-ID    : {app.client_id}"))
        self.stdout.write(self.style.WARNING(f"  Client-Secret: {new_secret}"))
        self.stdout.write(self.style.WARNING("=" * 60))
        self.stdout.write(self.style.ERROR("\n⚠️  Dieses Secret wird NICHT erneut angezeigt. Jetzt kopieren!\n"))
