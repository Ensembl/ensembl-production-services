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
from rest_framework.views import APIView
from rest_framework.response import Response
from mysql.connector import (connection)

class ListDatabases(APIView):
    """
    View to list all databases from a given server
    """
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        host = self.request.query_params.get('host', None)
        port = self.request.query_params.get('port', None)
        user = self.request.query_params.get('user', None)
        cnx = connection.MySQLConnection(user=user,
                                 host=host,
                                 port=port,
                                 database='information_schema')
        cursor = cnx.cursor()
        query = ("SELECT SCHEMA_NAME FROM SCHEMATA WHERE SCHEMA_NAME LIKE %s ORDER BY SCHEMA_NAME;")

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
        host = self.request.query_params.get('host', None)
        port = self.request.query_params.get('port', None)
        user = self.request.query_params.get('user', None)
        database = self.request.query_params.get('database', None)
        cnx = connection.MySQLConnection(user=user,
                                 host=host,
                                 port=port,
                                 database='information_schema')
        cursor = cnx.cursor()
        query = ("SELECT TABLE_NAME FROM TABLES WHERE TABLE_SCHEMA=%s AND TABLE_NAME LIKE %s ORDER BY TABLE_NAME;")

        table = self.request.query_params.get('table', None)
        table_list = []
        cursor.execute(query, (database, "%" + table + "%",))
        for (TABLE_NAME) in cursor:
            table_list.append(TABLE_NAME[0])
        cursor.close()
        cnx.close()
        return Response(table_list)