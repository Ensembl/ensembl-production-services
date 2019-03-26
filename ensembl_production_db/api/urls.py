# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from rest_framework_nested import routers
from rest_framework_swagger.views import get_swagger_view
from ensembl_production_db.router import CustomRouter

from ensembl_production_db.api import viewsets


# API router setup
router = routers.DefaultRouter(trailing_slash=False)
router_attrib = CustomRouter()
# Services URIs configuration

router.register(prefix=r'analysisdescription',
                viewset=viewsets.AnalysisDescriptionViewSet,
                base_name='analysisdescription')

router.register(prefix=r'attribtypes',
                viewset=viewsets.AttribTypeViewSet,
                base_name='attribtypes')

router_attrib.register(prefix=r'attrib',
                viewset=viewsets.AttribViewSet,
                base_name='attrib')

biotype_name_router = routers.SimpleRouter()
biotype_name_router.register(r'biotypes', viewsets.BiotypeNameViewSet)

biotype_object_type_router = routers.NestedSimpleRouter(biotype_name_router, r'biotypes', lookup='biotype')
biotype_object_type_router.register(r'types', viewsets.BiotypeObjectTypeViewSet, base_name='type')

schema_view = get_swagger_view(title='Ensembl Production DB API')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(router_attrib.urls)),
    url(r'^', include(biotype_object_type_router.urls)),
]
