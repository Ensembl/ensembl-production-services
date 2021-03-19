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
#   limitations under the License.

class ProductionPortalRouter:
    """
    A router to control all database operations on models in the
    auth application.
    """
    route_app_labels = {'auth', 'admin', 'contenttypes', 'sitetree', 'sessions', 'ensembl_production'}
    db_entry = 'default'

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return self.db_entry
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return self.db_entry
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth is involved.
        """
        if obj1._meta.app_label in self.route_app_labels or obj2._meta.app_label in self.route_app_labels:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth only appears in the 'auth_db'
        database.
        """
        if app_label in self.route_app_labels:
            return db == self.db_entry
        if 'target_db' in hints:
            return hints['target_db'] == self.db_entry
        if db == self.db_entry:
            return db == 'production'
        return False


class DbCopyRouter(ProductionPortalRouter):
    """
    A router to control all database operations on models in the ensembl db copy application.
    """
    route_app_labels = {'ensembl_dbcopy'}
    db_entry = 'dbcopy'


class MasterDbRouter(ProductionPortalRouter):
    """
    A router to control all database operations on models in the
    production application.
    """
    route_app_labels = {'ensembl_production_db'}
    db_entry = 'production'


class WebhelpRouter:
    """
    A router to control all database operations on models in the WebHelp application.
    """
    route_app_labels = {'ensembl_website'}
    db_entry = 'website'
