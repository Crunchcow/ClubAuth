# ClubAuth - Benutzerhandbuch

## Projektübersicht

**ClubAuth** ist die zentrale Authentifizierungsplattform für alle Vereinsanwendungen. Sie stellt sichere Anmeldung und Benutzerverwaltung für folgende Systeme bereit:

- Spielbetrieb (WOHU)
- Vereinsheimbuchung
- Tennisplatz-Buchung
- Kursanmeldung
- Schlüsselverwaltung

---

## Administrator-Bereich

### Zugangsdaten
- **URL:** `https://auth.westfalia-osterwick.de/admin/`
- **Login:** Mit Ihren Admin-Zugangsdaten

### Hauptfunktionen

#### 1. Benutzerverwaltung
Unter **Users → Users** können Sie:
- Neue Benutzer anlegen
- Bestehende Benutzer bearbeiten
- Passwörter zurücksetzen
- Benutzer aktivieren/deaktivieren

#### 2. Rollenverwaltung
Unter **Users → Rollenzuweisungen** können Sie:
- Benutzern spezifische Rollen für einzelne Anwendungen zuweisen
- Berechtigungen pro Anwendung verwalten

**Verfügbare Rollen pro Anwendung:**
- `spielbetrieb`: admin, koordinator, benutzer
- `vereinsheimbuchung`: admin, verwaltung, viewer
- `tenniscourts`: admin, benutzer
- `vereinsheim`: admin, viewer

#### 3. OAuth2 Anwendungen verwalten
Unter **OAuth2 Provider → Applications** können Sie:
- Neue Anwendungen registrieren
- Client-ID und Client Secret generieren
- Redirect-URIs konfigurieren
- Berechtigungen (Scopes) festlegen

---

## Benutzer-Anmeldung

### Für Endbenutzer
1. Rufen Sie eine der Vereinsanwendungen auf (z.B. Spielbetrieb)
2. Klicken Sie auf "Anmelden"
3. Sie werden automatisch zu ClubAuth weitergeleitet
4. Geben Sie Ihre E-Mail und Passwort ein
5. Nach erfolgreicher Anmeldung werden Sie zurück zur Anwendung geleitet

### Microsoft-Login (falls aktiviert)
Benutzer können sich auch mit ihrem Microsoft-Konto anmelden, wenn diese Option konfiguriert ist.

---

## Wichtige Administrationsaufgaben

### Neuen Benutzer anlegen
1. Admin-Bereich aufrufen
2. **Users → Users → Add user**
3. E-Mail, Vorname, Nachname eingeben
4. Passwort festlegen
5. Benutzer aktivieren ("Active" Häkchen setzen)
6. Rollen unter "Rollenzuweisungen" zuweisen

### Passwort zurücksetzen
1. Benutzer in der Liste auswählen
2. "Change password" klicken
3. Neues Passwort festlegen

### Neue Anwendung registrieren
1. **OAuth2 Provider → Applications → Add**
2. Name der Anwendung eingeben
3. Client type: "Confidential"
4. Authorization grant type: "Authorization code"
5. Redirect URI der Anwendung eintragen
6. Allowed scopes: `openid profile email roles`
7. Algorithm: RS256
8. Speichern und Client-ID/Secret an Anwendungsentwickler weitergeben

---

## Sicherheitshinweise

### Passwortrichtlinien
- Mindestens 8 Zeichen
- Empfehlung: Buchstaben, Zahlen und Sonderzeichen
- Regelmäßige Änderung empfohlen

### Zugriffssteuerung
- Prinzip der geringsten Rechte anwenden
- Inaktive Benutzer deaktivieren
- Rollen regelmäßig überprüfen

---

## Fehlerbehebung

### Häufige Probleme

**"Benutzer kann sich nicht anmelden"**
- Prüfen ob Benutzer aktiv ist
- Passwort zurücksetzen
- E-Mail-Adresse auf Korrektheit prüfen

**"Anwendung kann nicht verbinden"**
- Client-ID und Secret prüfen
- Redirect URI muss exakt übereinstimmen
- Anwendung muss in ClubAuth registriert sein

**"Rollen werden nicht übernommen"**
- Rollenzuweisung im Admin-Bereich prüfen
- Benutzer muss sich neu anmelden
- Cache der Anwendung leeren

---

## Technische Informationen

### Systemanforderungen
- Webbrowser mit JavaScript-Unterstützung
- Aktuelle Browser-Version empfohlen

### Support
Bei technischen Problemen wenden Sie sich an:
- Systemadministrator
- IT-Abteilung des Vereins

---

## Rechtliche Hinweise

### Datenschutz
- Alle Benutzerdaten werden verschlüsselt gespeichert
- Zugriff nur durch autorisierte Administratoren
- DSGVO-konforme Verarbeitung

### Haftung
Die Nutzung erfolgt auf eigene Gefahr. Für Schäden durch missbräuchliche Nutzung wird keine Haftung übernommen.

---

*Letzte Aktualisierung: April 2026*
