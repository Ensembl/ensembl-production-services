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
USER_DB_DATABASE=the_database
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
8. start nginx with ~/bin/nginx.sh start (install  nginx-extras for dependency ngx_http_perl_module)
```
        vi ./bin/nginx/nginx.conf 

        location /static/ {
            alias /usr/src/app/; # set path to static files directory
        }
```
```

 export APP_HOST_URL=http://127.0.0.1:8000  (production service url)
./bin/nginx.sh start

```

**All Done** go to `http://your_host/` and see.


Launch Production services with docker containers
================================================ 
- Set env variables

```
cp bin/.env.conf.sample bin/.env
vi bin/.env  (set required values)
```
- Create Network to access btw services
```
    docker network create  production_api 

```

- Build docker image for production services API  

```
sudo docker build -t production_service .
```
- Run Production service API

```
sudo docker run -it --rm --network=production_api --name productionportal -p 8000:8000  --env-file ./bin/.env production_service:latest
 - --add-host <mysqlhost>:<192.1.2.1> (add this param if mysqlhost is in different network)  
```

- build nginx docker image to serve static files 
```
    sudo docker build -t production_service_nginx -f Dockerfile.nginx  .          (its multi stage container with staticfiles)
    sudo docker run -it --rm --network=production_api --name productionnginx -e "APP_HOST_URL=http://productionportal:8000" production_service_nginx:latest

```