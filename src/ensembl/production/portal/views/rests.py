# See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework import routers

from ensembl.production.dbcopy.api import viewsets
from ensembl.production.masterdb.api.urls import router as prod_db_router, router_attrib

router = routers.SimpleRouter(trailing_slash=False)
router.register(prefix=r'requestjob',
                viewset=viewsets.RequestJobViewSet,
                basename='requestjob')

schema_view = get_schema_view(
    openapi.Info(
        title="Production REST APis snippets",
        default_version='v1',
        description="Production Portal REST",
        contact=openapi.Contact(email="ensembl-production@ebi.ac.uk"),
        license=openapi.License(name="Apache 2 License"),
    ),
    public=False,
    patterns=[
        path(f'api/dbcopy/', include(router.urls)),
        re_path(r'api/dbcopy/transfers/(?P<job_id>[^/.]+)$', viewsets.TransferLogView.as_view()),
        path(f'api/production_db/', include(router_attrib.urls)),
        path(f'api/production_db/', include(prod_db_router.urls)),
    ],
    permission_classes=(permissions.IsAuthenticated,),
)
