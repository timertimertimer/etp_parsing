#!/bin/sh

set -e

echo "Deploying app..."
playwright install chromium --with-deps
cd /var/www/app/docker/app/general_utils && alembic upgrade head
cd /var/www/app/docker/app && /usr/local/bin/python -m general_utils.db && /usr/local/bin/python -m general_utils.fedresurs

echo "App deployed!"