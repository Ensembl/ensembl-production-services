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
