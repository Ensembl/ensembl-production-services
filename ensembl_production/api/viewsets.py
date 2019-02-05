# -*- coding: utf-8 -*-

from rest_framework import viewsets

from ensembl_production.api.serializers import AnalysisDescriptionSerializer
from ensembl_production.models import WebData, AnalysisDescription
from .serializers import WebDataSerializer


class WebDataViewSet(viewsets.ModelViewSet):
    serializer_class = WebDataSerializer
    queryset = WebData.objects.using('production').all()


class AnalysisDescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = AnalysisDescriptionSerializer
    queryset = AnalysisDescription.objects.using('production').filter(is_current=1)
    lookup_field = 'logic_name'

