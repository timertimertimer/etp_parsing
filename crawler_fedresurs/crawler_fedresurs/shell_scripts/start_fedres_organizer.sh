#!/bin/bash
cd /home/parser/etp_parsing/crawler_fedresurs/crawler_fedresurs/shell_scripts && \
./docker_organizer_start.sh
cd /home/parser/etp_parsing && \
source env/bin/activate && \
cd /home/parser/etp_parsing/crawler_fedresurs && \
scrapy crawl fedres_organizer
cd /home/parser/etp_parsing/crawler_fedresurs/crawler_fedresurs/shell_scripts && \
./docker_organizer_stop.sh