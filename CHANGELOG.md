CHANGELOG - Ensembl Production Portal
=====================================

v4.2.3
------
- Added shortcut "New DBCopy Job" on top menu bar
- Integrated latest version of DBCopy (1.4.0) 
- Tweak UI - Main Layout
- Bumped dependencies versions
  - django-environ 0.4.5 => 0.7.0
  - django-cors-header 3.7.0 => 3.10.0
  - python-dotenv 0.18.0 => 0.19.0

v4.2.2
------
- BufFix: User multi group 500 and duplicated menu item list.


v4.2.1
------
- Bumped ensembl-dbcopy to 1.2.1 (hotfix)

v4.2
----
- Bumped ensembl-prodinf-dbcopy to 1.2

v4.1
----
- Bumped django-admin-inline-paginator version to 0.2
- Bumped ensembl-prodinf-dbcopy to 1.1
- Bumped ensembl-prodinf-webhelp to 1.1
- Bumped ensembl-prodinf-masterdb to 1.1
- Bumped ensembl-prodinf-jira to 1.1

v4.0
----
- Moved from initial production services monolithic application
- Added portables apps as modules
  - ensembl-prodinf-dbcopy (initially ensembl_dbcopy app)
  - ensembl-prodinf-webhelp (initially ensembl_intentions included app)
  - ensembl-prodinf-masterdb (initially ensembl_production_db included app)
  - ensembl-prodinf-jira (initially ensembl_intentions included app)
- Django standard layout / templates integration
- Changed namespace to `ensembl.production.portal`
  
