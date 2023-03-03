#   See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.import os
import os

import environ
import sys
from django.contrib.messages import constants as messages

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

environ.Env.read_env(os.environ.get("SERVICES_CONFIG_FILE", os.path.join(os.path.dirname(BASE_DIR), ".env")))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} - {process:d} ({thread:d}) - {module} --: {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} - {module} --: {message}',
            'style': '{',
        },
    },
    'loggers': {
        'asyncio': {
            'level': 'WARNING',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose' if DEBUG else 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG' if DEBUG else 'WARNING',
    }

}
if not DEBUG:
    ALLOWED_HOSTS = [
        '.ensembl-production.ebi.ac.uk'
    ]
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^http(s)?://\w+\.ebi\.ac\.uk$",
        r"^http(s)?://\w+\.ensembl.org$",
    ]

# Application definition

INSTALLED_APPS = [
    'dal_select2',
    'jazzmin',
    'django.contrib.admindocs',
    'django.contrib.admin',
    'ensembl.production.portal.apps.ProdAuthConfig',
    #'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_swagger',
    # Ensembl production apps
    'ensembl.production.portal',
    'ensembl.production.dbcopy',
    'ensembl.production.webhelp',
    'ensembl.production.masterdb',
    'ensembl.production.jira',
    'ensembl.production.metadata.admin',
    # Required utils
    'django_admin_inline_paginator',
    'ckeditor',
    'drf_yasg',
    'corsheaders',
    'dal'
]
# Override Metadata Verbose Name
# TODO remove this with updating the EnsemblMetadataConfig apps with proper label.
from ensembl.production.metadata.admin.apps import EnsemblMetadataConfig
EnsemblMetadataConfig. verbose_name = "Genome Metadata"


# Display Models APPs version in home page.
APP_LABEL_MAP = {
    'ensembl_dbcopy': 'ensembl-prodinf-dbcopy',
    'ensembl_website': 'ensembl-prodinf-webhelp ',
    'ensembl_production_db': 'ensembl-prodinf-masterdb',
    'ensembl_jira': 'ensembl-prodinf-jira'
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

X_FRAME_OPTIONS = "SAMEORIGIN"

# AUTHENTICATION_BACKENDS = ("django_python3_ldap.auth.LDAPBackend",)
APPEND_SLASH = True

ROOT_URLCONF = 'production_services.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR, 'ensembl', 'production', 'portal', 'templates'),
                 os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ensembl.production.portal.context_processors.portal'
            ],
            'libraries': {
                # make your file entry here.
                'filter_tags': 'ensembl.production.portal.templatetags.filter',
            }
        },
    }
]

WSGI_APPLICATION = 'production_services.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL', default='mysql://ensembl@127.0.0.1:3306/ensembl_production_services'),
    'production': env.db('PRODUCTION_DB_URL', default='mysql://ensembl@127.0.0.1:3306/ensembl_production'),
    'website': env.db('WEBHELP_DB_URL', default='mysql://ensembl@127.0.0.1:3306/ensembl_website'),
    'dbcopy': env.db('DBCOPY_DB_URL', default='mysql://ensembl@127.0.0.1:3306/db_copy'),
    'metadata': env.db('METADATA_DB_URL', default='mysql://ensembl@127.0.0.1:3306/ensembl_metadata_2020'),
    'ncbi': env.db('NCBI_DB_URL', default='mysql://ensembl@127.0.0.1:3306/ncbi_taxonomy'),
}

DATABASE_ROUTERS = [
    'ensembl.production.portal.routers.MasterDbRouter',
    'ensembl.production.portal.routers.WebhelpRouter',
    'ensembl.production.portal.routers.DbCopyRouter',
    'ensembl.production.portal.routers.ProductionPortalRouter',
    'ensembl.production.portal.routers.NcbiTaxonomyRouter',
    'ensembl.production.portal.routers.MetadataRouter',
]

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'

# mailing
LOGIN_REDIRECT_URL = '/'

MESSAGE_TAGS = {
    messages.DEBUG: 'info alert-info',
    messages.INFO: 'info alert-info',
    messages.SUCCESS: 'success alert-success',
    messages.WARNING: 'warning alert-warning',
    messages.ERROR: 'danger alert-danger',
}

IS_TESTING = sys.argv[1:2] == ['test']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' \
    if not DEBUG else 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default="ensembl-production@ebi.ac.uk")
MASTER_DB_ALERTS_EMAIL = env.str('MASTER_DB_ALERTS_EMAIL', default="ensembl-production@ebi.ac.uk")

EMAIL_CONFIG = env.email_url('EMAIl_URL', default='smtp://user:password@localhost:25')
vars().update(EMAIL_CONFIG)
LOGOUT_REDIRECT_URL = "/"
with open(os.path.join(os.path.dirname(BASE_DIR), 'VERSION')) as f:
    PORTAL_VERSION = f.read()

# USE_X_FORWARDED_HOST = True
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Production Portal",
    # Title on the brand, and login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Production",
    "site_brand": "Service portal",
    # square logo to use for your site, must be present in static files, used for favicon and brand on top left
    "site_logo": "/portal/img/2020e.svg",
    # Welcome text on the login screen
    "welcome_sign": "Welcome to Production services portal",
    # Copyright on the footer
    "copyright": "Ensembl Production Team (with Jazzmin)",
    # Field names on user model that contains avatar image
    "custom_js": 'portal/js/portal.js',
    "custom_css": 'portal/css/portal.css',
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Home", "url": "admin:index"},
        # external url that opens in a new window (Permissions can be added)
        {"name": "Support", "url": "https://www.ebi.ac.uk/panda/jira/projects/ENSPROD/issues/", "new_window": True},
        # model admin to link to (Permissions checked against model)
        {"name": "Api docs", "url": "rest_api_docs", "new_window": False},
        {"name": "New DBCopy Job", "url": "admin:ensembl_dbcopy_requestjob_add"},
        {"app": "ensembl_prodinf_portal", "permissions": ["auth.is_superuser"]},
    ],
    # Whether to display the side menu
    "show_sidebar": True,
    "related_modal_active": True,
    # Whether to aut expand the menu
    "navigation_expanded": False,
    # Icons that are used when one is not manually specified
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "ensembl_jira": "fas fa-bug",
        "ensembl_jira.JiraCredentials": "fas fa-key",
        "ensembl_jira.KnownBug": "fas fa-viruses",
        "ensembl_jira.RRBug": "fas fa-viruses",
        "ensembl_jira.Intention": "fas fa-lightbulb",
        "ensembl_dbcopy": "fas fa-copyright",
        "ensembl_dbcopy.RequestJob": "fas fa-copy",
        "ensembl_dbcopy.Host": "fas fa-server",
        "ensembl_dbcopy.TargetHostGroup": "fas fa-layer-group",
        "ensembl_production_db": "fas fa-brain",
        "ensembl_production_db.AnalysisDescription": "fas fa-microscope",
        "ensembl_production_db.MasterAttrib": "fas fa-eye-dropper",
        "ensembl_production_db.MasterAttribSet": "fas fa-capsules",
        "ensembl_production_db.MasterAttribType": "fas fa-link",
        "ensembl_production_db.MasterBiotype": "fas fa-dna",
        "ensembl_production_db.MasterExternalDb": "fas fa-database",
        "ensembl_production_db.WebData": "fas fa-cloud-meatball",
        "ensembl_production_db.MetaKey": "fas fa-meteor",
        "ensembl_metadata": "fas fa-microchip",
        "ensembl_metadata.Assembly": "fas fa-id-card",
        "ensembl_metadata.Attribute": "fas fa-paperclip",
        "ensembl_metadata.Dataset": "fas fa-database",
        "ensembl_metadata.Release": "fas fa-retweet",
        "ensembl_metadata.Organism": "fas fa-paw",
        "ensembl_metadata.OrganismGroup": "fas fa-users",
        "ensembl_website": "fas fa-life-ring",
        "ensembl_website.HelpLink": "far fa-life-ring",
        "ensembl_website.FaqRecord": "fas fa-question-circle",
        "ensembl_website.LookupRecord": "fas fa-search",
        "ensembl_website.MovieRecord": "fas fa-video",
        "ensembl_website.ViewRecord": "fas fa-file",
        "ensembl_prodinf_portal": "fas fa-archway",
        "ensembl_prodinf_portal.ProductionApp": "fas fa-concierge-bell",
        "ensembl_prodinf_portal.AppView": "fas fa-dragon"
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "changeform_format_overrides": {
        "auth.user": "vertical_tabs",
        "auth.group": "vertical_tabs",
    },
    "show_ui_builder": DEBUG,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": True,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": True,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": True,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "sandstone",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": False
}