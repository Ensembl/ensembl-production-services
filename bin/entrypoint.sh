#!/usr/bin/env sh

# Collect static files
echo "Collect static files"
python /home/portal/src/manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
echo "... for Ensembl Production"
python /home/portal/src/manage.py migrate ensembl_production_db --database production --fake-initial
echo "... for Ensembl Website Help"
python /home/portal/src/manage.py migrate ensembl_website --database website --fake-initial
echo "... for Ensembl DBCopy"
python /home/portal/src/manage.py migrate ensembl_dbcopy --database dbcopy --fake-initial
echo "... for Ensembl Genome Metadata"
python /home/portal/src/manage.py migrate ensembl_metadata --database metadata --fake-initial
echo "... for Ensembl Portal "
python /home/portal/src/manage.py migrate ensembl_prodinf_portal --database default --fake-initial
echo "... for Ensembl JIRA connector"
python /home/portal/src/manage.py migrate ensembl_jira --database default --fake-initial
echo "... for All the rest (Auth / Contenttypes etc...)"
python /home/portal/src/manage.py migrate --database default

# Start server
echo "Starting server"
gunicorn -c /home/portal/gunicorn.conf.py production_services.wsgi:application
