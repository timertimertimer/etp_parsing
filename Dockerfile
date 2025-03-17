FROM python:3.11-alpine

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
    unrar zip p7zip-full p7zip-rar \
    && rm -rf /var/cache/apk/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN deluser www-data \
    && addgroup -g $UID www-data \
    && adduser -u $UID -D -S -G www-data www-data \
    && echo "www-data ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

ENTRYPOINT ["top", "-b"]