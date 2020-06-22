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
# Import base config.
from production_services.settings import *
USE_TZ = True
# Database override
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('USER_DB_DATABASE', 'ensembl_tests'),
        'USER': os.getenv('USER_DB_USER', 'ensembl'),
        'PASSWORD': os.getenv('USER_DB_PASSWORD', 'ensembl'),
        'HOST': os.getenv('USER_DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('USER_DB_PORT', '3306'),
    },
    # FAKED DB for testing host schema retrieval for db_copy service
    'test_copy_db_1': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('USER_DB_DATABASE', 'ensembl_tests_db_copy_1'),
        'USER': os.getenv('USER_DB_USER', 'ensembl'),
        'PASSWORD': os.getenv('USER_DB_PASSWORD', 'ensembl'),
        'HOST': os.getenv('USER_DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('USER_DB_PORT', '3306'),
    },
    'test_copy_db_2': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('USER_DB_DATABASE', 'ensembl_tests_db_copy_2'),
        'USER': os.getenv('USER_DB_USER', 'ensembl'),
        'PASSWORD': os.getenv('USER_DB_PASSWORD', 'ensembl'),
        'HOST': os.getenv('USER_DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('USER_DB_PORT', '3306'),
    },
}

DATABASE_ROUTERS = []
