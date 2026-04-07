# ClubAuth – Deployment

## Projekt-Info

| | |
|---|---|
| **Stack** | Python + Django 4.2, django-oauth-toolkit (OIDC), social-auth-app-django |
| **Datenbank** | SQLite (`db.sqlite3`, lokal auf dem Server – **nicht im Repo**) |
| **Server** | `89.167.0.28` – Hostname: `WestfaliaOsterwick` (Ubuntu 24.04) |
| **App-Pfad** | `/var/www/clubauth/` |
| **Service** | systemd → `clubauth.service` (Port 8010) |
| **Nginx** | `/etc/nginx/sites-enabled/clubauth` |
| **URL** | `https://auth.westfalia-osterwick.de` |

---

## Update deployen (nach jedem `git push`)

```bash
ssh root@89.167.0.28 "cd /var/www/clubauth && git pull origin main && .venv/bin/pip install -r requirements.txt -q && .venv/bin/python manage.py migrate --noinput && .venv/bin/python manage.py collectstatic --noinput && systemctl restart clubauth && systemctl is-active clubauth"
```

Oder per `deploy.sh` (von lokal):
```bash
./deploy.sh
```

---

## Erstinstallation auf dem Server

### 1. Repository klonen & Umgebung einrichten

```bash
cd /var/www
git clone https://github.com/Crunchcow/ClubAuth.git clubauth
cd clubauth
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
nano .env
```

Mindestens setzen:
```env
SECRET_KEY=<zufälliger 50-Zeichen-String>
DEBUG=False
ALLOWED_HOSTS=auth.westfalia-osterwick.de,localhost
OIDC_RSA_PRIVATE_KEY_FILE=private.pem
```

### 3. RSA-Schlüssel für OIDC erzeugen

```bash
cd /var/www/clubauth
openssl genrsa -out private.pem 2048
chmod 600 private.pem
```

> **Wichtig:** `private.pem` ist im `.gitignore` und muss auf dem Server manuell erstellt werden.

### 4. Datenbank & statische Dateien

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
```

### 5. Ersten Superuser anlegen

```bash
.venv/bin/python manage.py createsuperuser
```

### 6. systemd-Service einrichten

```bash
cp /var/www/clubauth/clubauth.service /etc/systemd/system/clubauth.service
mkdir -p /var/log/clubauth
chown www-data:www-data /var/log/clubauth
systemctl daemon-reload
systemctl enable clubauth
systemctl start clubauth
systemctl status clubauth
```

### 7. Nginx konfigurieren

```bash
cp /var/www/clubauth/nginx.conf /etc/nginx/sites-enabled/clubauth
nginx -t && systemctl reload nginx
```

### 8. SSL-Zertifikat (Let's Encrypt)

```bash
certbot --nginx -d auth.westfalia-osterwick.de --non-interactive --agree-tos \
  -m lemke@westfalia-osterwick.de --redirect
```

---

## DNS-Eintrag

| Name | Typ | Wert |
|------|-----|------|
| `auth` | A | `89.167.0.28` |

---

## Erste OIDC-App registrieren (z. B. Spielbetrieb)

Im Django Admin unter `/admin/` → **OAuth2 Provider → Applications → Add**:

| Feld | Wert |
|------|------|
| Name | Spielbetrieb |
| Client type | Confidential |
| Authorization grant type | Authorization code |
| Redirect URIs | `https://spielbetrieb.westfalia-osterwick.de/oauth/callback` |
| Allowed scopes | `openid profile email roles` |
| Algorithm | RS256 |
| Skip authorization | ☐ (immer Zustimmungsscreen zeigen) |

Die generierten **Client ID** und **Client Secret** dann in der jeweiligen App als ENV-Variablen hinterlegen.

---

## Microsoft-Login aktivieren (optional)

Im Azure Portal eine App-Registrierung anlegen:
- Redirect URI: `https://auth.westfalia-osterwick.de/social-auth/complete/microsoft-oauth2/`
- API-Berechtigungen: `openid`, `email`, `profile`, `User.Read`

Dann in `/var/www/clubauth/.env`:
```env
MS_CLIENT_ID=<Application (client) ID>
MS_CLIENT_SECRET=<Client Secret>
MS_TENANT_ID=<Tenant ID oder "common">
```

Danach Service neu starten: `systemctl restart clubauth`

---

## Nützliche Befehle auf dem Server

```bash
# Service-Status
systemctl status clubauth

# Logs live
journalctl -u clubauth -f

# Nginx neu laden
nginx -t && systemctl reload nginx

# Datenbank-Shell
cd /var/www/clubauth && .venv/bin/python manage.py dbshell

# Neuen Admin-User anlegen
cd /var/www/clubauth && .venv/bin/python manage.py createsuperuser
```

---

## Rollen-Matrix

| App-Kennung | Verfügbare Rollen |
|-------------|------------------|
| `spielbetrieb` | `admin`, `koordinator`, `benutzer` |
| `vereinsheimbuchung` | `admin`, `verwaltung`, `viewer` |
| `tenniscourts` | `admin`, `benutzer` |
| `vereinsheim` | `admin`, `viewer` |

Rollen werden im Django Admin unter **Users → Benutzer → Rollenzuweisungen** verwaltet.

---

## Offene Punkte

- [ ] DNS-Eintrag `auth.westfalia-osterwick.de` → `89.167.0.28` setzen
- [ ] SSL via Certbot einrichten (Befehl s. o.)
- [ ] Spielbetrieb als erste OIDC-App registrieren
- [ ] Microsoft-Login konfigurieren (sobald Azure-App-Registrierung vorliegt)
