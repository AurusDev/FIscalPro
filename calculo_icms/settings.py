from pathlib import Path
import os
import dj_database_url  # 👈 novo

BASE_DIR = Path(__file__).resolve().parent.parent

# 🔑 Nunca deixa SECRET_KEY hardcoded em produção
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

DEBUG = os.getenv("DEBUG", "False") == "True"

# ⚠️ Ajuste: seu código estava ALLOWED_HOSTS: ["*"] (isso dá erro de sintaxe)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "calculo_icms.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "calculo_icms.wsgi.application"
ASGI_APPLICATION = "calculo_icms.asgi.application"

# 📦 Banco de dados
# Primeiro tenta usar DATABASE_URL (Heroku/Postgres),
# se não achar, cai pro SQLite local
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=False,
    )
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Recife"
USE_I18N = True
USE_TZ = True

# 📂 Arquivos estáticos
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Sessão – vamos guardar dataframe serializado
SESSION_COOKIE_AGE = 60 * 60 * 6  # 6h

# 🔐 CSRF (importante em produção)
CSRF_TRUSTED_ORIGINS = [
    "https://seuapp.herokuapp.com",   # ajuste para o domínio real
]
