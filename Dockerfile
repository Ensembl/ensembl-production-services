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
FROM python:3.8.13-alpine

# Install git
RUN apk update
RUN apk add git
RUN apk add --no-cache mariadb-dev
RUN apk add --no-cache musl-dev
RUN apk add --no-cache gcc
RUN apk add --no-cache libffi-dev
RUN adduser -D portal
USER portal
WORKDIR /home/portal

ENV PIP_ROOT_USER_ACTION=ignore
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=production_services.settings
ENV PATH="/home/portal/.local/bin:${PATH}"

COPY --chown=portal:portal requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN echo "cython<3" > /tmp/constraint.txt
RUN PIP_CONSTRAINT=/tmp/constraint.txt pip install --user -r requirements.txt

# Copy project files
COPY --chown=portal:portal . .
ENV PYTHONPATH=$PYTHONPATH:/home/portal/src

EXPOSE 8000
CMD ["/home/portal/bin/entrypoint.sh"]
# CMD ["sh"]