OJS LOM Plugin
==============

Workflow
--------

1. Activate plugin
2. Create table to store payload manifest info:
  - payload id
  - issue id
  - last updated
  - file
  - checksum
  - result
3. Plugin gets journal identifier from LOM staging server
  - stored in journal settings table
4. Plugin has hook to issues and articles
  - add conditions:
		+ published issue object is created which doesn't exist in LOM plugin table (published issue hook)
	- update conditions:
		+ article object created whose last_updated is newer than the issue in our LOM plugin table
5. In either case, an update consists of:
    - create uuid for published issue if published issue not in LOM plugin table
    - create issue archive
      + run issue xml export containing article file URLs (rather than BASE64)
      + parse export for article file URLs
      + copy files and issue xml to temporary directory, archive and copy archive to public directory
    - build atom manifest (from template?)
    - push manifest to staging server



