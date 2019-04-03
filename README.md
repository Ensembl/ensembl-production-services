# ensembl-production-services

INSTALL
=======

- clone the repo
- create a Python 3 virtual env
    - $: python3 -m venv .venv
    - $: source .venv/bin/activate
    - (.venv)$: pip install -r requirements.txt
    - (.venv)$: ./manage.py migrate
- copy config files
    - (.venv)$: cp bin/gunicorn.conf.py.sample bin/gunicorn.conf.py
    - (.venv)$: cp bin/nginx.conf.sample bin/nginx.conf

Create .env file (a .env.sample is available in checkout)
    - (.venv)$: cp bin/.env.conf.sample bin/.env
    - (.venv)$: vi bin/.env
    
    - put required parameters such as follow:
    
DJANGO_SETTINGS_MODULE=production_services.settings
PROD_DB_DATABASE=the_database
PROD_DB_USER=the_user
PROD_DB_HOST=the_host
PROD_DB_PORT=the_port
PROD_DB_PASSWORD=the_password
USER_DB_USER=the_user_database_user
USER_DB_PASSWORD=the_user_database_password
USER_DB_PORT=the_user_database_port
USER_DB_HOST=the_user_database_host

(update conf according to your needs - paths - hosts etc.)

- start gunicorn with 
    - (.venv)$: ./bin/gunicorn.sh start
- start nginx with ~/bin/nginx.sh start
    - (.venv)$: ./bin/nginx.sh start
    
*All Done* go to http://your_host/ and see.
