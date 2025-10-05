#!/bin/sh

set -e

export PYTHONPATH=/var/www

echo "Deploying app"
echo "Running migrations"
cd /var/www/app/db && uv run alembic upgrade head

echo "Running supervisord"
sudo supervisord -n
