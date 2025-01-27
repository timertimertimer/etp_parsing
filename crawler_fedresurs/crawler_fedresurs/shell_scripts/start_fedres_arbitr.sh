#!/bin/bash
cd /home/parser/etp_parsing/crawler_fedresurs/crawler_fedresurs/shell_scripts && \
./docker_arbitr_start.sh
cd /home/parser/etp_parsing && \
source env/bin/activate && \
cd /home/parser/etp_parsing/crawler_fedresurs && \
scrapy crawl fedres_arbitor
cd /home/parser/etp_parsing/crawler_fedresurs/crawler_fedresurs/shell_scripts && \
./docker_arbitr_stop.sh
