#!/bin/sh

set -e

sudo chown -R www-data:www-data /var/www/app

sudo find /var/www/app -type d -exec chmod 2755 {} \;
sudo find /var/www/app -type f -exec chmod 644 {} \;

sudo find /var/www/app/docker /var/www/app/deploy -type f -name "*.sh" -exec chmod +x {} \;

sudo chmod -R ug+rwx /var/www/app/storage