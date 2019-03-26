# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.5-alpine

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

ENV DJANGO_SETTINGS_MODULE=production_services.settings

RUN apk update && apk add bash

RUN set -e; \
        apk add --no-cache --virtual .build-deps \
                gcc \
                libc-dev \
                linux-headers \
                mariadb-dev \
                python3-dev;
# Set the working directory
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

