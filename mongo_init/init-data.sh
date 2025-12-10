#!/bin/bash

set -e
echo ">>>>>>>>>>> STARTING DATA IMPORT <<<<<<<<<<<"
mongoimport --host localhost --db blog_db --collection users --type json --file /docker-entrypoint-initdb.d/blog_db.users.json --jsonArray --drop
mongoimport --host localhost --db blog_db --collection blogs --type json --file /docker-entrypoint-initdb.d/blog_db.blogs.json --jsonArray --drop
mongoimport --host localhost --db blog_db --collection comments --type json --file /docker-entrypoint-initdb.d/blog_db.comments.json --jsonArray --drop
echo ">>>>>>>>>>> DATA IMPORT FINISHED <<<<<<<<<<<"