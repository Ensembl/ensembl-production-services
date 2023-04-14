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

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt

from ensembl.production.portal.models import ProductionApp, AllowedDatabaseModel

class ListAllowedDB(APIView):
    """
    View to list all allowed databases for a given division for handover service 
    """
    @csrf_exempt
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        """
        Return a list of allowed DBs
        """
        division = request.query_params.get('division')
        if division:
            division = division.capitalize()   
        try:
            results = ProductionApp.objects.filter(app_name__regex=f"{division}.*Handovers").values('allowed_data_types')
            allowed_db_list = [ res[val] for res in results for val in res.keys() ]
            allowed_db_type_names = [ db_name['name'] for db_name in AllowedDatabaseModel.objects.filter(id__in=allowed_db_list).values('name') ]
            return Response({'allowed_database_types': allowed_db_type_names})
       
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
