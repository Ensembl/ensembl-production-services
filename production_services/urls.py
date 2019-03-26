"""production_services URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from ensembl_production_db.api.urls import schema_view

urlpatterns = [
    # Production Admin
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^', admin.site.urls),
    # Production DB API
    url(r'^production_db/api/', include('ensembl_production_db.api.urls')),
    url(r'^production_db/api/schema', schema_view),
]

admin.site.site_header = "Ensembl Production Services"
admin.site.site_title = "Ensembl Production Services"
admin.site.index_title = "Welcome to Ensembl Production Services"
