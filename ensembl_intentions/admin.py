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
from django.contrib import admin
from .views import IntentionsView, IntentionView2

_admin_site_get_urls = admin.site.get_urls

def get_urls():
    from django.conf.urls import url
    urls = _admin_site_get_urls()
    urls += [
        url(r'^bugs/$', admin.site.admin_view(IntentionsView.as_view())),
        url(r'^intentions/$', admin.site.admin_view(IntentionView2.as_view()))
    ]
    return urls


admin.site.get_urls = get_urls