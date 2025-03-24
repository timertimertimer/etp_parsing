FROM python:3.12-bookworm

ARG USER
ARG UID

WORKDIR /var/www/app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
        curl \
        cron \
        sudo \
        default-mysql-client \
        supervisor \
        git \
        zip \
        p7zip-full \
        unrar-free \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN deluser www-data && \
    addgroup --gid $UID www-data && \
    adduser --uid $UID --disabled-password --ingroup www-data www-data && \
    echo "www-data ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN touch /var/log/etp_parsing_output.log && chmod 777 /var/log/etp_parsing_output.log

COPY ./cron /var/spool/cron/crontabs/www-data
RUN chmod 600 /var/spool/cron/crontabs/www-data && chmod 700 /var/spool/cron/crontabs

COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER www-data

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
