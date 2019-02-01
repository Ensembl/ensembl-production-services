# -*- coding: utf-8 -*-

from rest_framework import viewsets

from ensembl_production.models import WebData
from .serializers import WebDataSerializer


class WebDataViewSet(viewsets.ModelViewSet):
    serializer_class = WebDataSerializer
    queryset = WebData.objects.all()
