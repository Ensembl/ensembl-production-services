CHANGELOG - Ensembl Production Portal
=====================================
4.4.5
-----
- Updated apps to latest version
  - ensembl-prodinf-masterdb@git+https://github.com/Ensembl/ensembl-prodinf-masterdb.git@1.2.5 (new fields)
- Updated Docker Container:
  - Finalize migration automation on startup (ENTRYPOINT=/home/portal/bin/entrypoint.sh)
  - Accept CMD extra param CMD=["TEST"] (local test or unreleased dependencies)
    - Load extra "requirement-test.txt" requirements on startup. (unreleased)
    - run manage.py runserver 0.0.0.0:8000 with loaded CSS / Javasacripts.  

4.4.4
-----
- Updated apps to latest version
  - ensembl-metadata-admin@git+https://github.com/Ensembl/ensembl-metadata-admin.git@0.0.8
  - ensembl-prodinf-masterdb@git+https://github.com/Ensembl/ensembl-prodinf-masterdb.git@1.2.4 (new fields)

4.4.3
-----

- Updated apps to latest version
  - ensembl-metadata-admin@git+https://github.com/Ensembl/ensembl-metadata-admin.git@0.0.4
  - ensembl-prodinf-masterdb@git+https://github.com/Ensembl/ensembl-prodinf-masterdb.git@1.2.3
  - ensembl-prodinf-jira@git+https://github.com/Ensembl/ensembl-prodinf-jira.git@2.0.3

- Added api endpoint to access new production metadata 
   - api/genome_metadata/
  
- Fix for analysis description API, default JSON EXTRACT fails to filter with json object

4.4.1
-----

- Updated apps to latest version
  - ensembl-prodinf-dbcopy@git+https://github.com/Ensembl/ensembl-prodinf-dbcopy.git@1.7.0
  - ensembl-prodinf-webhelp@git+https://github.com/Ensembl/ensembl-prodinf-webhelp.git@1.1.1
  - ensembl-prodinf-masterdb@git+https://github.com/Ensembl/ensembl-prodinf-masterdb.git@1.2.0
  - ensembl-prodinf-jira@git+https://github.com/Ensembl/ensembl-prodinf-jira.git@1.1.1
- Added new metadata-admin apps:
  - ensembl-metadata-admin@git+https://github.com/Ensembl/ensembl-metadata-admin.git@0.0.2
- Updated Jazzmin to latest
- Updated Django to latest 3.2.17

4.4.0
-----
- Display apps version for Ensembl managed modules
- Removed obsolete view
- Bumped `ensembl-prodinf-dbcopy` to 1.6.0
- Copyright updates
- Updates App stylesheets
- Removed obsolete field in FlaskApps table `app_config_params`
- Renamed `django.contrib.auth` verbose name (better display in left menu)

4.3.0
------
- Updated dependencies version in requirements.txt
- New Version of DBCopy app
- App can now have relative path based on portal base url http://ensembl-services.ensembl.org 

4.2.4
------
- bugfix: pop-up opening
- Top Menu: 
  - Production REST endpoints swagger docs (ProductionDB and DBCopy)
  - models docs link (top right corner)
- CHANGELOG github link added.
- bugfix: prodinf-jira bumped to 1.1.1 to fix issue with intentions retrieval

4.2.3
------
- Added shortcut "New DBCopy Job" on top menu bar
- Integrated latest version of DBCopy (1.4.0) 
- Tweak UI - Main Layout
- Bumped dependencies versions
  - django-environ 0.4.5 => 0.7.0
  - django-cors-header 3.7.0 => 3.10.0
  - python-dotenv 0.18.0 => 0.19.0

4.2.2
------
- BufFix: User multi group 500 and duplicated menu item list.


4.2.1
------
- Bumped ensembl-dbcopy to 1.2.1 (hotfix)

4.2
----
- Bumped ensembl-prodinf-dbcopy to 1.2

4.1
----
- Bumped django-admin-inline-paginator version to 0.2
- Bumped ensembl-prodinf-dbcopy to 1.1
- Bumped ensembl-prodinf-webhelp to 1.1
- Bumped ensembl-prodinf-masterdb to 1.1
- Bumped ensembl-prodinf-jira to 1.1

4.0
----
- Moved from initial production services monolithic application
- Added portables apps as modules
  - ensembl-prodinf-dbcopy (initially ensembl_dbcopy app)
  - ensembl-prodinf-webhelp (initially ensembl_intentions included app)
  - ensembl-prodinf-masterdb (initially ensembl_production_db included app)
  - ensembl-prodinf-jira (initially ensembl_intentions included app)
- Django standard layout / templates integration
- Changed namespace to `ensembl.production.portal`
  
