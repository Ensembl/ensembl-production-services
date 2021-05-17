# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.8.9

RUN useradd --create-home appuser
USER appuser

#create virtual env
RUN python -m venv /home/appuser/venv
ENV PATH="/home/appuser/venv/bin:$PATH"

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

ENV DJANGO_SETTINGS_MODULE=production_services.settings

# Set the working directory
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY --chown=appuser . /usr/src/app

RUN cp ./bin/gunicorn.conf.py.sample ./bin/gunicorn.conf.py 

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install gunicorn~=20.1.0
RUN pip install -r requirements.txt


ENV PYTHONPATH=$PYTHONPATH:/usr/src/app/src
EXPOSE 8000
CMD ["/home/appuser/venv/bin/gunicorn", "-c",  "/usr/src/app/bin/gunicorn.conf.py", "production_services.wsgi:application"]
