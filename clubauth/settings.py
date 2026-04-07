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
    "users",
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

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/profile/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

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
}

# ---------------------------------------------------------------------------
# Social Auth — Microsoft (optional, nur aktiv wenn MS_CLIENT_ID gesetzt ist)
# ---------------------------------------------------------------------------
SOCIAL_AUTH_MICROSOFT_OAUTH2_KEY = config("MS_CLIENT_ID", default="")
SOCIAL_AUTH_MICROSOFT_OAUTH2_SECRET = config("MS_CLIENT_SECRET", default="")
SOCIAL_AUTH_MICROSOFT_OAUTH2_TENANT_ID = config("MS_TENANT_ID", default="common")
SOCIAL_AUTH_MICROSOFT_OAUTH2_SCOPE = ["openid", "email", "profile", "User.Read"]

SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/profile/"
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
