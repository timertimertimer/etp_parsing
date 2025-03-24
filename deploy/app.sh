#!/bin/sh

set -e

echo "Deploying app..."
playwright install chromium --with-deps
cd /var/www/app/docker/app/general_utils && alembic upgrade head
cd /var/www/app/docker/app/general_utils && /usr/local/bin/python db.py && /usr/local/bin/python fedresurs.py

echo "App deployed!"