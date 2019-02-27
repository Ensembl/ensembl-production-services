# -*- coding: utf-8 -*-


class ProductionRouter:
    """
    A router to control all database operations on models in the
    production application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read production models go to production.
        """
        if model._meta.app_label == 'ensembl_production':
            return 'production'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write production models go to production.
        """
        if model._meta.app_label == 'ensembl_production':
            return 'production'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the production app is involved.
        """
        if obj1._meta.app_label == 'ensembl_production' or \
                obj2._meta.app_label == 'ensembl_production':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the production app only appears in the 'production'
        database.
        """
        if app_label == 'ensembl_production':
            return db == 'production'
        return None
