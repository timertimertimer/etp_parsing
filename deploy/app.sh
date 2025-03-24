#!/bin/sh

set -e

echo "Deploying app..."
playwright install chromium --with-deps
cd /var/www/app/docker/app/general_utils && alembic revision --autogenerate -m "Initial migration" && alembic upgrade head

echo "App deployed!"