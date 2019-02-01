# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from rest_framework import routers

from ensembl_production.api import viewsets
from rest_framework_swagger.views import get_swagger_view
# API router setup
router = routers.DefaultRouter(trailing_slash=False)
# Services URIs configuration
router.register(prefix=r'web_data',
                viewset=viewsets.WebDataViewSet,
                base_name='web-data')

schema_view = get_swagger_view(title='Pastebin API')

urlpatterns = [
    url(r'^', include(router.urls)),
]
