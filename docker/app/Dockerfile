FROM python:3.12-alpine

ARG USER
ARG UID

WORKDIR /var/www/app

RUN apk update \
    && apk add --no-cache \
        curl \
        sudo \
        mysql-client \
        supervisor \
        git \
        unrar \
        zip \
        p7zip \
        p7zip-rar \
    && rm -rf /var/cache/apk/*


COPY . .
RUN pip install --no-cache-dir -r requirements.txt

RUN deluser www-data \
    && addgroup -g $UID www-data \
    && adduser -u $UID -D -S -G www-data www-data \
    && echo "www-data ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

COPY ./docker/app/cron /etc/crontabs/www-data
COPY ./docker/app/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh

USER www-data

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
