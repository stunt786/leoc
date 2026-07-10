#Migration to Live Server
**Migrate the frontend code and some db changes in the live server without loosing existing data in the db.

##Server Details
192.168.101.10
username: thalaramun
password: thalaraMUN@3
 
application location directory: /home/thalaramun/leoc
**Aplication is using docker on port 5002, and requires sudo access for any changes on server so always use sudo with docker commands
docker containers: leoc-app & leoc-db

## Migration
**First backup existing app with db
**Only mirate new files/changed files and db changes only, keeping existing data. 
**Make proper backup and test the migration on a staging environment before applying to production
**Fix any issues that arises while migrating with existing data.. the existing data should properly work with new files and db withpout any issues.

