#!/usr/bin/env python
# .. See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

FROM nginx:1.20.0-alpine-perl
RUN apk add --no-cache nginx-module-perl
RUN rm /etc/nginx/conf.d/default.conf
COPY ./bin/nginx/nginx.conf /etc/nginx/nginx.conf
CMD ["/bin/sh", "-c", "exec nginx -g 'daemon off;';"]
EXPOSE 80
