#!/bin/sh

set -e

sudo chown -R www-data:www-data /var/www/app

sudo find /var/www/app/docker /var/www/app/deploy -type f -name "*.sh" -exec chmod +x {} \;

sh /var/www/app/deploy/full.sh

sudo supervisord -n