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
from rest_framework.routers import Route, SimpleRouter


class ProductionRouter:
    """
    A router to control all database operations on models in the
    production application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read production models go to production.
        """
        if model._meta.app_label == 'ensembl_production_db':
            return 'production'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write production models go to production.
        """
        if model._meta.app_label == 'ensembl_production_db':
            return 'production'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the production production_services is involved.
        """
        if obj1._meta.app_label == 'ensembl_production_db' or \
                obj2._meta.app_label == 'ensembl_production_db':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the production production_services only appears in the 'production'
        database.
        """
        #if 'target_db' in hints:
        #    return hints['target_db'] == "ensembl_production_db"
        if app_label == 'ensembl_production_db':
            return db == 'production'
        return None


class CustomRouter(SimpleRouter):
    """
    A router for read-only APIs, which doesn't use trailing slashes.
    """
    routes = [
        Route(
            url=r'^{prefix}$',
            mapping={'get': 'list', 'post': 'create'},
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        )
    ]
