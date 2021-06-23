CHANGELOG - Ensembl Production Portal
=====================================

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
  