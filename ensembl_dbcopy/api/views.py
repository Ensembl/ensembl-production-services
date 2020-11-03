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

from ensembl_dbcopy.models import Host
import logging


logger = logging.getLogger(__name__)


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


class ListDatabases(APIView):
    """
    View to list all databases from a given server
    """

    def get(self, request, format=None):
        """
        Return a list of all schema names
        """
        hostname = request.query_params.get('host')
        port = request.query_params.get('port')
        if not (hostname and port):
            return Response('Required parameters: host, port',
                            status=status.HTTP_400_BAD_REQUEST)
        dbname_filter = request.query_params.get('search', '').strip('%')
        dbnames_matches = request.query_params.getlist('matches[]')
        try:
            db_engine = get_engine(hostname, port)
        except RuntimeError as e:
            return Response([])
        database_list = sa.inspect(db_engine).get_schema_names()
        if dbnames_matches:
            database_set = set(database_list)
            dbnames_set = set(dbnames_matches)
            result = database_set.intersection(dbnames_set)
        else:
            try:
                filter_db_re = re.compile(dbname_filter)
            except re.error as e:
                return Response([])
            result = filter(filter_db_re.search, database_list)
        return Response(result)


class ListTables(APIView):
    """
    View to list all databases from a given server
    """

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        hostname = request.query_params.get('host')
        port = request.query_params.get('port')
        database = request.query_params.get('database', '').strip('%')
        if not (hostname and port and database):
            return Response('Required parameters: host, port, database',
                            status=status.HTTP_400_BAD_REQUEST)
        table_name_filter = request.query_params.get('search', '')
        table_name_matches = request.query_params.getlist('matches[]')
        try:
            filter_table_re = re.compile(table_name_filter)
        except re.error as e:
            return Response([])
        try:
            db_engine = get_engine(hostname, port)
        except RuntimeError as e:
            return Response([])
        try:
            table_list = sa.inspect(db_engine).get_table_names(schema=database)
        except sa.exc.OperationalError as e:
            return Response([])
        if table_name_matches:
            table_set = set(table_list)
            table_names_set = set(table_name_matches)
            result = table_set.intersection(table_names_set)
        else:
            result = filter(filter_table_re.search, table_list)
        return Response(result)
