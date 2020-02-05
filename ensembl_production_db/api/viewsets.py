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

from ensembl_production_db.api.serializers import *
from ensembl_production_db.models import *
from .serializers import WebDataSerializer


class WebDataViewSet(viewsets.ModelViewSet):
    serializer_class = WebDataSerializer
    queryset = WebData.objects.all()


class AnalysisDescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = AnalysisDescriptionSerializerUser
    queryset = AnalysisDescription.objects.filter()
    lookup_field = 'logic_name'


class BiotypeNameViewSet(viewsets.ModelViewSet):
    serializer_class = BiotypeSerializerUser
    queryset = MasterBiotype.objects.filter()
    lookup_field = 'name'


class BiotypeObjectTypeViewSet(viewsets.ModelViewSet):
    serializer_class = BiotypeSerializerUser
    lookup_field = 'object_type'
    lookup_url_kwarg = 'type'

    def get_queryset(self):
        return MasterBiotype.objects.filter(name=self.kwargs['biotype_name'])

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = BiotypeSerializerUser(queryset, many=True)
        if len(serializer.data) == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.data)


class AttribTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AttribTypeSerializerUser
    queryset = MasterAttribType.objects.all()
    lookup_field = 'code'


class AttribViewSet(viewsets.ModelViewSet):
    serializer_class = AttribSerializerUser
    queryset = MasterAttrib.objects.all()
    lookup_field = 'value'
