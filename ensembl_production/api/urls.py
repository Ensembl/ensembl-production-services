# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from rest_framework_nested import routers

from ensembl_production.api import viewsets
from rest_framework_swagger.views import get_swagger_view
# API router setup
router = routers.DefaultRouter(trailing_slash=False)
# Services URIs configuration
router.register(prefix=r'web_data',
                viewset=viewsets.WebDataViewSet,
                base_name='web-data')

router.register(prefix=r'analysis',
                viewset=viewsets.AnalysisDescriptionViewSet,
                base_name='analysis')

router.register(prefix=r'attribtype',
                viewset=viewsets.AttribTypeViewSet,
                base_name='attribtype')

biotype_name_router = routers.SimpleRouter()
biotype_name_router.register(r'biotype', viewsets.BiotypeNameViewSet)

biotype_object_type_router = routers.NestedSimpleRouter(biotype_name_router, r'biotype',lookup='name')
biotype_object_type_router.register(r'object_type', viewsets.BiotypeObjectTypeViewSet,base_name='object_type')

schema_view = get_swagger_view(title='Pastebin API')
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(biotype_object_type_router.urls)),
]
