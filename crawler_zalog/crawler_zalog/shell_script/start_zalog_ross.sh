#!/bin/bash
sleep 2
mydir=$HOME
#cache_dir=$mydir/etp_parsing/crawler_be_two_be/.scrapy/

sleep 5
cd $mydir/etp_parsing/crawler_zalog/crawler_zalog/shell_script/ && \
./docker_zalog_ross_start.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_zalog
scrapy crawl zalog_ross
sleep 1
cd $mydir/etp_parsing/crawler_zalog/crawler_zalog/shell_script/ && \
./docker_zalog_ross_stop.sh