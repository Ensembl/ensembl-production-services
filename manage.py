#!/usr/bin/env python
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
import configparser


def read_env():
    """
    Reads a INI file named .env in the same directory manage.py is invoked and
    loads it as environment variables.
    Note: At least one section must be present. If the environment variable
    DJANGO_ENV is not set then the [DEFAULT] section will be loaded.
    More info: https://docs.python.org/3/library/configparser.html
    """
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read('./.env')
    section = os.environ.get("DJANGO_ENV", "DEFAULT")

    for var, value in config[section].items():
        os.environ.setdefault(var, value)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "production_services.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    read_env()
    execute_from_command_line(sys.argv)
