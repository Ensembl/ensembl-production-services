# -*- coding: utf-8 -*-

from rest_framework import viewsets

from ensembl_production.api.serializers import AnalysisDescriptionSerializer, BiotypeSerializer, AttribTypeSerializer
from ensembl_production.models import WebData, AnalysisDescription, MasterBiotype, MasterAttribType
from .serializers import WebDataSerializer,escape_perl_string, PerlFieldElementSerializer
from rest_framework.response import Response
from rest_framework import status


class WebDataViewSet(viewsets.ModelViewSet):
    serializer_class = WebDataSerializer
    queryset = WebData.objects.all()


class AnalysisDescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = AnalysisDescriptionSerializer
    queryset = AnalysisDescription.objects.filter(is_current=1)
    lookup_field = 'logic_name'


class BiotypeNameViewSet(viewsets.ModelViewSet):
    serializer_class = BiotypeSerializer
    queryset = MasterBiotype.objects.filter(is_current=1)
    lookup_field = 'name'

class BiotypeObjectTypeViewSet(viewsets.ModelViewSet):
    serializer_class = BiotypeSerializer
    lookup_field = 'object_type'
    lookup_url_kwarg = 'type'

    def get_queryset(self):
        return MasterBiotype.objects.filter(name=self.kwargs['biotype_name'])

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = BiotypeSerializer(queryset, many=True)
        if len(serializer.data) is 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.data)


class AttribTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AttribTypeSerializer
    queryset = MasterAttribType.objects.filter(is_current=1)
    lookup_field = 'code'
