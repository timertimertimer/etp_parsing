#!/bin/sh
set -e

export PYTHONPATH=/var/www

echo "Deploying app"
echo "Running migrations"

echo "Waiting for MySQL at $DB_HOST:$DB_PORT..."
until mysqladmin ping -h "$DB_HOST" -P "$DB_PORT" --silent; do
    echo "MySQL is unavailable - sleeping 2s"
    sleep 2
done

cd /var/www/app/db && alembic upgrade head

if [ "$RUN_CRON" = "1" ]; then
    echo "Running supervisord with cron..."
    sudo supervisord -n
else
    echo "Running app once..."
    cd /var/www/app && python main.py
fi
