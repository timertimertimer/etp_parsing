#!/bin/bash
sleep 2
mydir=$HOME
cache_dir=$mydir/etp_parsing/crawler_akosta/.scrapy/

sleep 5
cd $mydir/etp_parsing/crawler_akosta/crawler_akosta/shell_script/ && \
./docker_akosta_start.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_akosta
scrapy crawl akosta
sleep 1
cd $mydir/etp_parsing/crawler_akosta/crawler_akosta/shell_script/ && \
./docker_akosta_stop.sh



