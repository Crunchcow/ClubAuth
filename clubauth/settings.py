import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "oauth2_provider",
    "social_django",
    "users.apps.UsersConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "users.middleware.ForcePasswordChangeMiddleware",
]

ROOT_URLCONF = "clubauth.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "clubauth.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_USER_MODEL = "users.CustomUser"

AUTHENTICATION_BACKENDS = [
    "social_core.backends.microsoft.MicrosoftOAuth2",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "de-de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# E-Mail / SMTP
# ---------------------------------------------------------------------------
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="ClubAuth <noreply@westfalia-osterwick.de>")
PASSWORD_RESET_TIMEOUT = 3600  # Link gültig 1 Stunde

LOGIN_REDIRECT_URL = config("LOGIN_REDIRECT_URL", default="/profile/")
LOGIN_URL = "/accounts/login/"
LOGOUT_REDIRECT_URL = "/accounts/login/"
ALLOWED_REDIRECT_HOSTS = ["hub.westfalia-osterwick.de", "auth.westfalia-osterwick.de"]

# Eindeutiger Cookie-Name, damit kein Konflikt mit anderen Apps auf derselben IP
SESSION_COOKIE_NAME = config("SESSION_COOKIE_NAME", default="clubauth_sessionid")
CSRF_COOKIE_NAME    = config("CSRF_COOKIE_NAME",    default="clubauth_csrftoken")

# Cookie-Einstellungen (HTTP - Hub und ClubAuth beide auf HTTP)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=False, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=False, cast=bool)
SESSION_COOKIE_SAMESITE = config("SESSION_COOKIE_SAMESITE", default="Lax")
CSRF_COOKIE_SAMESITE = config("CSRF_COOKIE_SAMESITE", default="Lax")

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://89.167.0.28:8099,http://auth.westfalia-osterwick.de",
    cast=Csv(),
)

USE_X_FORWARDED_HOST = True

# ---------------------------------------------------------------------------
# OIDC / OAuth2-Provider (django-oauth-toolkit)
# ---------------------------------------------------------------------------
_rsa_key_path = BASE_DIR / config("OIDC_RSA_PRIVATE_KEY_FILE", default="private.pem")
_rsa_key = _rsa_key_path.read_text() if _rsa_key_path.exists() else ""

OAUTH2_PROVIDER = {
    "OIDC_ENABLED": True,
    "OIDC_RSA_PRIVATE_KEY": _rsa_key,
    "SCOPES": {
        "openid": "OpenID Connect",
        "profile": "Profilinformationen (Name)",
        "email": "E-Mail-Adresse",
        "roles": "App-spezifische Rollen",
    },
    "DEFAULT_SCOPES": ["openid", "profile", "email", "roles"],
    "OAUTH2_VALIDATOR_CLASS": "users.oauth2_validator.CustomOAuth2Validator",
    "ACCESS_TOKEN_EXPIRE_SECONDS": 3600,       # 1 Stunde
    "REFRESH_TOKEN_EXPIRE_SECONDS": 604800,    # 7 Tage
    "ROTATE_REFRESH_TOKEN": True,
    # PKCE nur für Public Clients erzwingen; Confidential Clients (mit Secret) brauchen kein PKCE
    "PKCE_REQUIRED": False,
    # Secrets im Klartext speichern (alle Apps nutzen Plaintext-Secrets in .env)
    "HASH_CLIENT_SECRET": False,
}

# ---------------------------------------------------------------------------
# Social Auth — Microsoft (optional, nur aktiv wenn MS_CLIENT_ID gesetzt ist)
# ---------------------------------------------------------------------------
SOCIAL_AUTH_MICROSOFT_OAUTH2_KEY = config("MS_CLIENT_ID", default="")
SOCIAL_AUTH_MICROSOFT_OAUTH2_SECRET = config("MS_CLIENT_SECRET", default="")
SOCIAL_AUTH_MICROSOFT_OAUTH2_TENANT_ID = config("MS_TENANT_ID", default="common")
SOCIAL_AUTH_MICROSOFT_OAUTH2_SCOPE = ["openid", "email", "profile", "User.Read"]

SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/profile/"

# Hub status API: CORS für den Hub erlauben
HUB_ORIGIN = config("HUB_ORIGIN", default="http://89.167.0.28:8088")

# Interner API-Key für app-to-app Kommunikation (z.B. Kursanmeldung sync)
INTERNAL_API_KEY = config("INTERNAL_API_KEY", default="")

# Webhook-URL der Kursanmeldung für automatischen User-Sync
KURSANMELDUNG_WEBHOOK_URL = config("KURSANMELDUNG_WEBHOOK_URL", default="")

# Webhook-URL der Vereinsheimbuchung für automatischen User-Sync
VEREINSHEIMBUCHUNG_WEBHOOK_URL = config("VEREINSHEIMBUCHUNG_WEBHOOK_URL", default="")

SOCIAL_AUTH_LOGIN_ERROR_URL = "/accounts/login/?error=social"
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = "/profile/"

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "users.pipeline.associate_by_email",       # Verknüpft mit bestehendem Account
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "users.pipeline.save_microsoft_oid",       # OID aus Azure speichern
)

SOCIAL_AUTH_USER_FIELDS = ["email", "first_name", "last_name"]

# ---------------------------------------------------------------------------
# Sicherheits-Einstellungen (nur in Produktion aktiv)
# ---------------------------------------------------------------------------
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # Kann per ENV deaktiviert werden bis SSL/DNS eingerichtet ist
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
    CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
