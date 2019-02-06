# -*- coding: utf-8 -*-

from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ensembl_production.api.serializers import AnalysisDescriptionSerializer, BiotypeSerializer, AttribTypeSerializer
from ensembl_production.models import WebData, AnalysisDescription, MasterBiotype, MasterAttribType
from .serializers import WebDataSerializer



class WebDataViewSet(viewsets.ModelViewSet):
    serializer_class = WebDataSerializer
    queryset = WebData.objects.using('production').all()


class AnalysisDescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = AnalysisDescriptionSerializer
    queryset = AnalysisDescription.objects.using('production').filter(is_current=1)
    lookup_field = 'logic_name'

class BiotypeNameViewSet(viewsets.ModelViewSet):
    serializer_class = BiotypeSerializer
    queryset = MasterBiotype.objects.using('production').filter(is_current=1)

class BiotypeObjectTypeViewSet(viewsets.ModelViewSet):
    serializer_class = BiotypeSerializer
    lookup_field = 'object_type'
    def get_queryset(self):
        return MasterBiotype.objects.filter(name=self.kwargs['name_pk'])

class AttribTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AttribTypeSerializer
    queryset = MasterAttribType.objects.using('production').filter(is_current=1)
    lookup_field = 'code'