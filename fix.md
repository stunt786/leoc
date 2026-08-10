#Migration to Live Server
**Migrate the frontend, backend code changed  & db columns without destructing functionality

##Server Details
192.168.101.10
username: thalaramun
password: thalaraMUN@3
 
application location directory: /home/thalaramun/leoc
**Aplication is using docker on port 5002, and requires sudo access for any changes on server so always use sudo with docker commands
docker containers: leoc-app & leoc-db

## Migration Note
just only migrate latest update code, backend code and db .
Make sure the new migration should not delete old reccords and since tables are merged in updates, the app should work with old records with  new db schema
make proper migration plan, backup and test

