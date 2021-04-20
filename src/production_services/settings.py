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

import sys
from django.contrib.messages import constants as messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'l2!hqu2y5o3q7yxfkzfw=ivn(kg_tz!^1l8l%36&$u*eid%4!g')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

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

ALLOWED_HOSTS = ['*']

# CORS settings
CORS_ALLOWED_ORIGINS = [
    'https://www.ebi.ac.uk',
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.ebi\.ac\.uk$",
    r"^https://\w+\.ensembl.org$",
]

# Application definition

INSTALLED_APPS = [
    'dal_select2',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_swagger',
    # Ensembl production apps
    'ensembl.production.dbcopy',
    'ensembl.production.webhelp',
    'ensembl.production.masterdb',
    'ensembl.production.jira',
    'ensembl.production.portal',
    # Required utils
    'django_admin_inline_paginator',
    # 'multiselectfield',
    'ckeditor',
    'drf_yasg',
    # 'sitetree',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# AUTHENTICATION_BACKENDS = ("django_python3_ldap.auth.LDAPBackend",)
APPEND_SLASH = True

ROOT_URLCONF = 'production_services.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
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
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('USER_DB_DATABASE', 'ensembl_production_services'),
        'USER': os.getenv('USER_DB_USER', 'ensembl'),
        'PASSWORD': os.getenv('USER_DB_PASSWORD', ''),
        'HOST': os.getenv('USER_DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('USER_DB_PORT', '3306'),
        'OPTIONS': {}
    },
    'production': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('PROD_DB_DATABASE', 'ensembl_production'),
        'USER': os.getenv('PROD_DB_USER', 'ensembl'),
        'PASSWORD': os.getenv('PROD_DB_PASSWORD', ''),
        'HOST': os.getenv('PROD_DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('PROD_DB_PORT', '3306'),
        'OPTIONS': {
            # Tell MySQLdb to connect with 'utf8mb4' character set
            'charset': os.getenv('PROD_DB_CHARSET', 'utf8mb4'),
            "init_command": "SET default_storage_engine=MYISAM",
        }
    },
    'website': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('WEBSITE_DB_DATABASE', 'ensembl_website'),
        'USER': os.getenv('WEBSITE_DB_USER', 'ensembl'),
        'PASSWORD': os.getenv('WEBSITE_DB_PASSWORD', ''),
        'HOST': os.getenv('WEBSITE_DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('WEBSITE_DB_PORT', '3306'),
        'OPTIONS': {
            # Tell MySQLdb to connect with 'utf8mb4' character set
            'charset': os.getenv('WEBSITE_DB_CHARSET', 'utf8mb4'),
            "init_command": "SET default_storage_engine=MYISAM",
        }
    },
    'dbcopy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_COPY_DATABASE', 'ensembl_dbcopy'),
        'USER': os.getenv('DB_COPY_USER', 'ensembl'),
        'PASSWORD': os.getenv('DB_COPY_PASSWORD', ''),
        'HOST': os.getenv('DB_COPY_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_COPY_PORT', '3306'),
        'OPTIONS': {
            "init_command": "SET default_storage_engine=InnoDB",
        }
    },
}

DATABASE_ROUTERS = [
    'ensembl.production.portal.routers.MasterDbRouter',
    'ensembl.production.portal.routers.WebhelpRouter',
    'ensembl.production.portal.routers.DbCopyRouter',
    'ensembl.production.portal.routers.ProductionPortalRouter',
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

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' if not DEBUG else 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = "ensembl-production@ebi.ac.uk"
EMAIL_HOST = 'localhost'
LOGOUT_REDIRECT_URL = "/"
## Set to have request.get_host() give precedence to X-Forwarded-Host over Host
# USE_X_FORWARDED_HOST = True

JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Production Portal",
    # Title on the brand, and login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Production",
    # square logo to use for your site, must be present in static files, used for favicon and brand on top left
    "site_logo": "/portal/img/2020e.svg",
    # Welcome text on the login screen
    "welcome_sign": "Welcome to Production services portal",
    # Copyright on the footer
    "copyright": "<a href=\"https://ensembl.org\">Ensembl.org</a><span>>>>> One portal to rule them all.<<<</span>",
    # Field name on user model that contains avatar image
    "custom_js": 'portal/js/portal.js',
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Home", "url": "admin:index"},
        # external url that opens in a new window (Permissions can be added)
        {"name": "Support", "url": "https://www.ebi.ac.uk/panda/jira/projects/ENSPROD/issues/", "new_window": True},
        # model admin to link to (Permissions checked against model)
        # {"model": "ensembl_prodinf_portal.AppView"},
        # short link to Production Apps
        {"name": "Self-Services", "url": "admin:ensembl_prodinf_portal_appview_changelist", "new_window": False},
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
    "navbar_small_text": False,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "cerulean",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success"
    }
}
