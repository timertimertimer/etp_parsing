#!/bin/bash
mydir=$HOME
cd $mydir/etp_parsing/crawler_sberbank/crawler_sberbank/shell_script && \
./docker_sber_local_start.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_sberbank
scrapy crawl sberbank
sleep 1
cd $mydir/etp_parsing/crawler_sberbank/crawler_sberbank/shell_script && \
./docker_sber_stop.sh