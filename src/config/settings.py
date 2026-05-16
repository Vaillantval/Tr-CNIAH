#src\config\settings.py

import os
import dj_database_url
from pathlib import Path
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG') == '1'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Ajouter automatiquement les domaines Railway au démarrage
_RAILWAY_SAFE_HOSTS = ['healthcheck.railway.app']
for _h in _RAILWAY_SAFE_HOSTS:
    if _h not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_h)

for _var in ('RAILWAY_PUBLIC_DOMAIN', 'RAILWAY_PRIVATE_DOMAIN'):
    _domain = os.environ.get(_var, '').strip()
    if _domain and _domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_domain)

# CSRF_TRUSTED_ORIGINS pour les domaines Railway (HTTPS requis en prod)
CSRF_TRUSTED_ORIGINS = []
for _h in ALLOWED_HOSTS:
    if _h not in ('localhost', '127.0.0.1', '0.0.0.0', 'healthcheck.railway.app') and '.' in _h:
        for _scheme in ('https://', 'http://'):
            _origin = f'{_scheme}{_h}'
            if _origin not in CSRF_TRUSTED_ORIGINS:
                CSRF_TRUSTED_ORIGINS.append(_origin)


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    # Third party apps
    'ckeditor',
    'ckeditor_uploader',
    'django_cleanup.apps.CleanupConfig',
    'axes',
    'simple_history',
    'django_celery_results',

    # Local apps
    'apps.news',
    'apps.advertisements',
    'apps.contact',
    'apps.core',
    'apps.members',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "templates",
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# Railway injecte DATABASE_URL automatiquement.
# Fallback sur les variables individuelles pour le dev local (docker-compose).
_DATABASE_URL = os.environ.get('DATABASE_URL')
if _DATABASE_URL:
    DATABASES = {'default': dj_database_url.parse(_DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'cniah_db'),
            'USER': os.environ.get('POSTGRES_USER', 'cniah_user'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'cniah_password'),
            'HOST': os.environ.get('DB_HOST', 'db'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'America/Port-au-Prince'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CKEditor Configuration
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ],
        'height': 300,
        'width': '100%',
    },
    'full': {
        'toolbar': 'full',
        'height': 400,
    },
}

# Jazzmin Configuration (Admin moderne)
JAZZMIN_SETTINGS = {
    "site_title": "CNIAH Admin",
    "site_header": "CNIAH",
    "site_brand": "Administration CNIAH",
    "welcome_sign": "Bienvenue sur l'administration du CNIAH",
    "copyright": "CNIAH",
    "search_model": "members.User",
    "topmenu_links": [
        {"name": "Accueil", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Voir le site", "url": "/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "members.user": "fas fa-user-tie",
        "core.banner": "fas fa-image",
        "core.serviceblock": "fas fa-th-large",
        "core.proposition": "fas fa-file-pdf",
        "core.engineeringbranch": "fas fa-industry",
        "core.newsletter": "fas fa-envelope",
        "core.membershipdocument": "fas fa-file-contract",
        # Nouveaux modèles de documents
        "core.documentcategory": "fas fa-folder-tree",
        "core.referencedocument": "fas fa-file-pdf",
        "core.videoresource": "fas fa-video",
        "core.imagegallery": "fas fa-images",
        # Autres modèles
        "news.newsarticle": "fas fa-newspaper",
        "advertisements.sponsor": "fas fa-handshake",
        "advertisements.advertisement": "fas fa-ad",
        "contact.contactmessage": "fas fa-envelope",
        "contact.professionalrequest": "fas fa-user-tie",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "members.user": "collapsible",
        "auth.group": "vertical_tabs"
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-navy",
    "accent": "accent-primary",
    "navbar": "navbar-navy navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Formats de fichiers autorisés pour les documents
ALLOWED_DOCUMENT_EXTENSIONS = [
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar'
]

# Formats de vidéo autorisés
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'mov', 'avi', 'mkv', 'webm']

# Taille max des fichiers (en bytes)
MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_VIDEO_SIZE = 500 * 1024 * 1024    # 500 MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024     # 10 MB

# ==================== DJANGO-AXES (brute-force protection) ====================
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.5  # 30 minutes
AXES_LOCKOUT_TEMPLATE = None
AXES_RESET_ON_SUCCESS = True

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Model User personnalisé
AUTH_USER_MODEL = 'members.User'

# Redirections auth
LOGIN_URL = '/membres/connexion/'
LOGIN_REDIRECT_URL = '/membres/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Email
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', '1') == '1'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@cniah.ht')

# URL du site pour génération de liens (emails, QR codes)
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8002')

# ==================== PLOPPLOP (MonCash / NatCash) ====================
PLOPPLOP_CLIENT_ID = os.environ.get('PLOPPLOP_CLIENT_ID', '')

# ==================== TAUX DE CHANGE ====================
EXCHANGERATE_API_KEY = os.environ.get('EXCHANGERATE_API_KEY', '')
# Taux HTG/USD de secours si l'API est indisponible (mis à jour manuellement si besoin)
EXCHANGERATE_HTG_FALLBACK = float(os.environ.get('EXCHANGERATE_HTG_FALLBACK', '132.0'))

# Emails de notification interne — accepte plusieurs adresses séparées par virgule
# Ex: secretariat@cniah.ht,info@cniah.ht
ADMIN_NOTIFY_EMAIL = [
    e.strip() for e in os.environ.get('ADMIN_NOTIFY_EMAIL', '').split(',') if e.strip()
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'apps': {
            'handlers': ['console'],
            'level': os.environ.get('LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ==================== SÉCURITÉ PRODUCTION ====================
if not DEBUG:
    # Railway termine TLS à la périphérie et transmet X-Forwarded-Proto: https
    # Ce header permet à Django de savoir que la requête originale était HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Ne pas forcer le redirect SSL ici — Railway le fait déjà au niveau edge.
    # Activer ce redirect ferait échouer le health check interne de Railway (HTTP → 301).
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ==================== CACHE ====================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'cniah-cache',
    }
}

CACHE_TTL_NEWS = 5 * 60       # 5 minutes pour les actualités
CACHE_TTL_SPONSORS = 60 * 60  # 1 heure pour les sponsors

# ==================== CELERY ====================
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE