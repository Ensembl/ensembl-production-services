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
import os
from production_services.settings import *

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False if DEBUG else True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# Database override
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('TEST_DB_DATABASE', 'production_services'),
        'USER': os.getenv('TEST_DB_USER', 'ensembl'),
        'PASSWORD': os.getenv('TEST_DB_PASSWORD', None),
        'HOST': 'localhost',
        'PORT': 3306,
    }
}
# Fixtures are timestamped with this parameter.
USE_TZ = True
DATABASE_ROUTERS = []

