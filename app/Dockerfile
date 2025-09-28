FROM ghcr.io/astral-sh/uv:python3.13-bookworm

ARG USER
ARG UID

WORKDIR /var/www/app

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Container needs some tools
RUN echo "deb http://deb.debian.org/debian/ bookworm main contrib non-free" > /etc/apt/sources.list.d/debian.list \
    && apt-get update && apt-get install -y \
        curl \
        cron \
        sudo \
        default-mysql-client \
        supervisor \
        git \
        zip \
        p7zip-full \
        unrar \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv pip install -e . --system

COPY . .

# Create user and set permissions
RUN deluser www-data 2>/dev/null || true && \
    addgroup --gid $UID www-data && \
    adduser --uid $UID --disabled-password --ingroup www-data www-data && \
    echo "www-data ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Create log file with proper permissions
RUN touch /var/log/etp_parsing_output.log && chmod 777 /var/log/etp_parsing_output.log

# Copy cron jobs
COPY ./cron /var/spool/cron/crontabs/www-data
RUN chmod 600 /var/spool/cron/crontabs/www-data && chmod 700 /var/spool/cron/crontabs

# Copy and make entrypoint executable
COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set proper ownership
RUN chown -R www-data:www-data /app

USER www-data

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
