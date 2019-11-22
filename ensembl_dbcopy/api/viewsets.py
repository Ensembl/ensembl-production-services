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
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from ensembl_dbcopy.api.serializers import *
from ensembl_dbcopy.models import *


class RequestJobViewSet(viewsets.ModelViewSet):
    serializer_class = RequestJobListSerializer
    queryset = RequestJob.objects.all()
    pagination_class = None
    lookup_field = 'job_id'


    def get_serializer_class(self):
        if self.action == 'list':
            return RequestJobListSerializer
        else:
            return RequestJobDetailSerializer

class HostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HostSerializer
    lookup_field = 'name'

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `name` query parameter in the URL.
        """
        queryset = Host.objects.all()
        host_name = self.request.query_params.get('name', None)
        if host_name is not None:
            queryset = queryset.filter(name__contains=host_name)
        return queryset