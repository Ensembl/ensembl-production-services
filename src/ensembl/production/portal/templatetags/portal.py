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
import logging
from typing import List, Dict

import pkg_resources
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from jazzmin.settings import get_settings
from jazzmin.templatetags.jazzmin import register
from jazzmin.utils import make_menu

from ensembl.production.portal.models import AppView

logger = logging.getLogger(__name__)


@register.simple_tag
def get_top_menu(user: AbstractUser, admin_site: str = "admin") -> List[Dict]:
    """
    Produce the menu for the top nav bar
    """
    options = get_settings()
    menu = make_menu(user, options.get("topmenu_links", []), options, admin_site=admin_site)
    children = [
        {"name": child.app_name, "url": child.get_admin_url(), "children": None, "icon": "portal/img/logo.png"}
        for child in AppView.objects.user_apps(user)
    ]
    menu.insert(len(menu) - 2 if len(menu) > 2 else 1,
                {
                    "name": "Self Services",
                    "url": "#",
                    "children": children,
                    "icon": options["default_icon_children"],
                }
                )
    return menu


@register.simple_tag
def app_version(app):
    print(app['app_label'])
    if app['app_label'] in settings.APP_LABEL_MAP:
        try:
            package = pkg_resources.get_distribution(settings.APP_LABEL_MAP[app['app_label']])
            return f"v{package.version}"
        except pkg_resources.DistributionNotFound:
            print("not Found", app['app_label'])
            pass
    return ""
