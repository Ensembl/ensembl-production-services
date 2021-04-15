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
    'sitetree',
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
                'ensembl.production.portal.context_processors.context_app_info'
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
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# mailing
LOGIN_REDIRECT_URL = '/'
# LOGIN_URL = 'app/admin/login'

MESSAGE_TAGS = {
    messages.DEBUG: 'info alert-info',
    messages.INFO: 'info alert-info',
    messages.SUCCESS: 'success alert-success',
    messages.WARNING: 'warning alert-warning',
    messages.ERROR: 'danger alert-danger',
}

IS_TESTING = sys.argv[1:2] == ['test']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = "ensembl-production@ebi.ac.uk"
EMAIL_HOST = 'localhost'
LOGOUT_REDIRECT_URL = "/"
## Set to have request.get_host() give precedence to X-Forwarded-Host over Host
# USE_X_FORWARDED_HOST = True

BATON = {
    'SITE_HEADER': 'Production Portal',
    'SITE_TITLE': 'Ensembl!',
    'INDEX_TITLE': 'Ensembl Production Services portal',
    'COPYRIGHT': '©2021 <a href="https://ensembl.org">Ensembl.org</a><br/>>>> One portal to rule them all.<<<',
    'POWERED_BY': 'Production Team',
    'SUPPORT_HREF': 'https://www.ebi.ac.uk/panda/jira/projects/ENSPROD/issues/',
    'COLLAPSABLE_USER_AREA': False,
    'MENU_ALWAYS_COLLAPSED': False,
    'LOGIN_SPLASH': '/static/portal/img/splash.jpg',
    'GRAVATAR_DEFAULT_IMG': 'retro',
    'CHANGELIST_FILTERS_IN_MODAL': True,
    'CHANGELIST_FILTERS_ALWAYS_OPEN': False,
    'CHANGELIST_FILTERS_FORM': True,
}
JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Production Portal",
    # Title on the brand, and login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Production",
    # square logo to use for your site, must be present in static files, used for favicon and brand on top left
    "site_logo": "/portal/img/logo.png",
    # Welcome text on the login screen
    "welcome_sign": "Welcome to Production services portal",
    # Copyright on the footer
    "copyright": "<a href=\"https://ensembl.org\">Ensembl.org</a><span>>>>> One portal to rule them all.<<<</span>",
    # Field name on user model that contains avatar image
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        # external url that opens in a new window (Permissions can be added)
        {"name": "Support", "url": "https://www.ebi.ac.uk/panda/jira/projects/ENSPROD/issues/", "new_window": True},
        # model admin to link to (Permissions checked against model)
        {"model": "auth.User"},
        # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app": "ensembl.production.portal"},
    ],
    # Whether to display the side menu
    "show_sidebar": True,
    # Whether to aut expand the menu
    "navigation_expanded": False,
    # Icons that are used when one is not manually specified
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
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": True,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "darkly",
    "dark_mode_theme": "slate",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success"
    }
}