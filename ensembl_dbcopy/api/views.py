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
from mysql.connector import (connection)
from rest_framework.response import Response
from rest_framework.views import APIView

from ensembl_dbcopy.models import Host


def mysql_connection(query_params={}):
    # host = query_params.get('host', None)
    host = Host.objects.filter(name=query_params.get('host', None),
                               port=query_params.get('port', None)).first()
    # port = query_params.get('port', None)
    # user = query_params.get('user', None)
    password = query_params.get('password', None)
    if host:
        return connection.MySQLConnection(user=host.mysql_user,
                                          host=host.name,
                                          port=host.port,
                                          password=password,
                                          database='information_schema')


class ListDatabases(APIView):
    """
    View to list all databases from a given server
    """

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        cnx = mysql_connection(request.query_params)
        cursor = cnx.cursor()
        query = "SELECT SCHEMA_NAME FROM SCHEMATA WHERE SCHEMA_NAME LIKE %s ORDER BY SCHEMA_NAME;"

        database = self.request.query_params.get('database', None)
        database_list = []
        cursor.execute(query, ("%" + database + "%",))
        for (SCHEMA_NAME) in cursor:
            database_list.append(SCHEMA_NAME[0])
        cursor.close()
        cnx.close()
        return Response(database_list)


class ListTables(APIView):
    """
    View to list all databases from a given server
    """

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        cnx = mysql_connection(request.query_params)
        cursor = cnx.cursor()
        query = "SELECT TABLE_NAME FROM TABLES WHERE TABLE_SCHEMA=%s AND TABLE_NAME LIKE %s ORDER BY TABLE_NAME;"

        database = self.request.query_params.get('database', None)
        table = self.request.query_params.get('table', None)
        table_list = []
        cursor.execute(query, (database, "%" + table + "%",))
        for (TABLE_NAME) in cursor:
            table_list.append(TABLE_NAME[0])
        cursor.close()
        cnx.close()
        return Response(table_list)
