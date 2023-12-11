#!/usr/bin/env sh

# Collect static files
echo "CMD PARAM: '$1'"
if [ "$1" = "TEST" ]; then
  pip install -r /home/portal/requirements-test.txt
  echo "Collect static files"
  python /home/portal/src/manage.py collectstatic --noinput
fi
# Apply database migrations
echo "Apply database migrations"
echo "... for Ensembl Production"
python /home/portal/src/manage.py migrate ensembl_production_db --noinput --database production --fake-initial
echo "... for Ensembl Website Help"
python /home/portal/src/manage.py migrate ensembl_website --noinput --database website --fake-initial
echo "... for Ensembl DBCopy"
python /home/portal/src/manage.py migrate ensembl_dbcopy --noinput --database dbcopy --fake-initial
echo "... for Ensembl Genome Metadata"
python /home/portal/src/manage.py migrate ensembl_metadata --noinput --database metadata --fake-initial
echo "... for Ensembl Portal "
python /home/portal/src/manage.py migrate ensembl_prodinf_portal --noinput --database default --fake-initial
echo "... for Ensembl JIRA connector"
python /home/portal/src/manage.py migrate ensembl_jira --noinput --database default --fake-initial
echo "... for All the rest (Auth / Contenttypes etc...)"
python /home/portal/src/manage.py migrate --noinput --database default

# Start server
echo "Starting server"
if [ "$1" = "TEST" ]; then
  python /home/portal/src/manage.py runserver 0.0.0.0:8000
else
  gunicorn -c /home/portal/gunicorn.conf.py production_services.wsgi:application
fi