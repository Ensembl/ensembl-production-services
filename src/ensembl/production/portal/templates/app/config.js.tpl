angular.module('app.config', [])
    .constant('CONFIG', {
        'FLASK_APP': '{{ flask_app.app_name }}',
        'FLASK_PATH': '/app/{{ flask_app.app_prod_url }}/',
        {% for key, value in flask_app.app_config_params.items %}
	    '{{ key }}': '{{ value }}',
	    {% empty %}
    	'LIVE_URI': 'mysql://ensembl@ensro@127.0.0.1:3306/',
        'STAGING_URI': 'mysql://ensembl@ensro@127.0.0.1:3306/',
        'COMPARA_URI': 'mysql:///ensembl@127.0.0.1:3306/ensembl_compara_master',
        'PROD_URI': 'mysql://ensembl@127.0.0.1:3306/ensembl_production',
        'HC_SRV_URL': 'http://127.0.0.1:5001/',
        'DB_SRV_URL': 'http://127.0.0.1:5002/',
        'URI_USER': 'ensembl',
        'COPY_SOURCE_USER': 'ensembl',
        'COPY_TARGET_USER': 'ensembl',
        'DATA_FILES_PATH' : '~/data_files/',
        'METADATA_SRV_URL': 'http://127.0.0.1:5003/',
        'HANDOVER_SRV_URL': 'http://127.0.0.1:5004/',
        'WEBSITE_NAME': 'Local Service'
	    {% endfor %}
    });
