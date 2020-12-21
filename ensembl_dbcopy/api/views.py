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
import re
from functools import lru_cache
import sqlalchemy as sa
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from ensembl_dbcopy.models import Host, Dbs2Exclude
import logging


logger = logging.getLogger(__name__)


def make_excluded_schemas():
    schemas = set()
    def closure():
        if not schemas:
            schemas.update(Dbs2Exclude.objects.values_list('table_schema', flat=True))
        return schemas
    return closure

get_excluded_schemas = make_excluded_schemas()


@lru_cache(maxsize=None)
def get_engine(hostname, port, password=''):
    host = Host.objects.filter(name=hostname, port=port).first()
    if not host:
        raise RuntimeError('No host corresponding to %s:%s' % (hostname, port))
    uri = 'mysql://{}:{}@{}:{}'.format(host.mysql_user,
                                       password,
                                       host.name,
                                       host.port)
    return sa.create_engine(uri, pool_recycle=3600)


def get_database_set(hostname, port, name_filter='', name_matches=[]):
    try:
        db_engine = get_engine(hostname, port)
    except RuntimeError as e:
        raise ValueError('Invalid hostname: {} or port: {}'.format(hostname, port)) from e
    database_list = sa.inspect(db_engine).get_schema_names()
    excluded_schemas = get_excluded_schemas()
    if name_matches:
        database_set = set(database_list)
        names_set = set(name_matches)
        return database_set.difference(excluded_schemas).intersection(names_set)
    else:
        try:
            filter_db_re = re.compile(name_filter)
        except re.error as e:
            raise ValueError('Invalid name_filter: {}'.format(name_filter)) from e
        return set(filter(filter_db_re.search, database_list)).difference(excluded_schemas)


def get_table_set(hostname, port, database, name_filter='', name_matches=[]):
    try:
        filter_table_re = re.compile(name_filter)
    except re.error as e:
        raise ValueError('Invalid name_filter: {}'.format(name_filter)) from e
    try:
        db_engine = get_engine(hostname, port)
    except RuntimeError as e:
        raise ValueError('Invalid hostname: {} or port: {}'.format(hostname, port)) from e
    try:
        table_list = sa.inspect(db_engine).get_table_names(schema=database)
    except sa.exc.OperationalError as e:
        raise ValueError('Invalid database: {}'.format(database)) from e
    excluded_schemas = get_excluded_schemas()
    if name_matches:
        table_set = set(table_list)
        table_names_set = set(name_matches)
        return table_set.difference(excluded_schemas).intersection(table_names_set)
    return set(filter(filter_table_re.search, table_list)).difference(excluded_schemas)


class ListDatabases(APIView):
    """
    View to list all databases from a given server
    """

    def get(self, request, *args, **kwargs):
        """
        Return a list of all schema names
        """
        hostname = kwargs.get('host')
        port = kwargs.get('port')
        name_filter = request.query_params.get('search', '').replace('%', '.*').replace('_', '.')
        name_matches = request.query_params.getlist('matches[]')
        try:
            result = get_database_set(hostname, port, name_filter, name_matches)
        except ValueError as e:
            return Response(str(e), status=status.HTTP_404_NOT_FOUND)
        return Response(result)


class ListTables(APIView):
    """
    View to list all tables from a given database
    """

    def get(self, request, *args, **kwargs):
        """
        Return a list of tables
        """
        hostname = kwargs.get('host')
        port = kwargs.get('port')
        database = kwargs.get('database')
        name_filter = request.query_params.get('search', '')
        name_matches = request.query_params.getlist('matches[]')
        try:
            result = get_table_set(hostname, port, database, name_filter, name_matches)
        except ValueError as e:
            return Response(str(e), status=status.HTTP_404_NOT_FOUND)
        return Response(result)

