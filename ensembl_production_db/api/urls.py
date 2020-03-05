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
from django.conf.urls import url, include
from rest_framework_nested import routers
from rest_framework_swagger.views import get_swagger_view

from ensembl_production_db.api import viewsets
from ensembl_production_db.router import CustomRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Production DB API snippets",
      default_version='v1',
      description="Production DB Api Description",
      contact=openapi.Contact(email="ensembl-production@ebi.ac.uk"),
      license=openapi.License(name="Apache 2 License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# API router setup
router = routers.DefaultRouter(trailing_slash=False)
router_attrib = CustomRouter()
# Services URIs configuration

router.register(prefix=r'analysisdescription',
                viewset=viewsets.AnalysisDescriptionViewSet,
                basename='analysisdescription')

router.register(prefix=r'attribtypes',
                viewset=viewsets.AttribTypeViewSet,
                basename='attribtypes')

router_attrib.register(prefix=r'attrib',
                       viewset=viewsets.AttribViewSet,
                       basename='attrib')

biotype_name_router = routers.SimpleRouter()
biotype_name_router.register(r'biotypes', viewsets.BiotypeNameViewSet)

biotype_object_type_router = routers.NestedSimpleRouter(biotype_name_router, r'biotypes', lookup='biotype')
biotype_object_type_router.register(r'types', viewsets.BiotypeObjectTypeViewSet, basename='type')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(router_attrib.urls)),
    url(r'^', include(biotype_object_type_router.urls)),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^docs/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
