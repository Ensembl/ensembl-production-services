# ensembl_production_api

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

(update conf according to your needs - paths - hosts etc.)

- start gunicorn with 
    - (.venv)$: ./bin/gunicorn.sh start
- start nginx with ~/bin/nginx.sh start
    - (.venv)$: ./bin/nginx.sh start
    
*All Done* go to http://your_host/ and see.