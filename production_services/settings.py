# -*- coding: utf-8 -*-
"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import os
import sys
from django.contrib.messages import constants as messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'l2!hqu2y5o3q7yxfkzfw=ivn(kg_tz!^1l8l%36&$u*eid%4!g')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'jet',
    'ensembl_production.apps.EnsemblProductionConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_swagger',
    'ensembl_production_db.apps.EnsemblProductionDbConfig',
    'ensembl_website.apps.EnsemblWebsiteConfig',
    'multiselectfield',
    'ckeditor',
    'crispy_forms',
    'drf_yasg',
]

MIDDLEWARE = [
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
        'DIRS': [os.path.join(BASE_DIR, 'ensembl_production/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
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
        'OPTIONS': {
            "init_command": "SET default_storage_engine=MYISAM",
        }
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
            'charset': 'utf8mb4',
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
            'charset': 'utf8mb4',
            "init_command": "SET default_storage_engine=MYISAM",
        }
    }
}

DATABASE_ROUTERS = [
    'ensembl_production.router.AuthRouter',
    'ensembl_production_db.router.ProductionRouter',
    'ensembl_website.router.WebsiteRouter'
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# mailing
LOGIN_REDIRECT_URL = '/'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}
