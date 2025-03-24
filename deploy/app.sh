#!/bin/sh

set -e

echo "Deploying app..."
playwright install chromium --with-deps
cd /var/www/app/docker/app/general_utils && alembic upgrade head

echo "App deployed!"