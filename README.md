# ensembl-production-services

INSTALL
=======

1. clone the repo
2. create a Python 3 virtual env
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
3. copy config files
```
cp bin/gunicorn.conf.py.sample bin/gunicorn.conf.py
cp bin/nginx.conf.sample bin/nginx.conf
```
4. Create .env file (a .env.sample is available in checkout)
```
cp bin/.env.conf.sample bin/.env
vi bin/.env
```
5. put required parameters such as follow:
```
DJANGO_SETTINGS_MODULE=production_services.settings
PROD_DB_DATABASE=the_database
PROD_DB_USER=the_user
PROD_DB_HOST=the_host
PROD_DB_PORT=the_port
PROD_DB_PASSWORD=the_password
WEBSITE_DB_DATABASE=the_database
WEBSITE_DB_USER=the_user
WEBSITE_DB_HOST=the_host
WEBSITE_DB_PORT=the_port
WEBSITE_DB_PASSWORD=the_password
DB_COPY_DATABASE=the_database
DB_COPY_USER=the_user
DB_COPY_HOST=the_host
DB_COPY_PORT=the_port
DB_COPY_PASSWORD=the_password
USER_DB_USER=the_user_database_user
USER_DB_PASSWORD=the_user_database_password
USER_DB_PORT=the_user_database_port
USER_DB_HOST=the_user_database_host
```

(update conf according to your needs - paths - hosts etc.)

6. migrate to propagate changes
```
source ./bin/.env
export $(cut -d= -f1 ./bin/.env)
./manage.py migrate
```

7. start gunicorn with
```
./bin/gunicorn.sh start
```
8. start nginx with ~/bin/nginx.sh start
```
./bin/nginx.sh start
```

**All Done** go to `http://your_host/` and see.
