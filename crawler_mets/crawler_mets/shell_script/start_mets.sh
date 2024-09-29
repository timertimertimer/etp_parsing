#!/bin/bash
mydir=$HOME
cd $mydir/etp_parsing/crawler_mets/crawler_mets/shell_script && \
./docker_start_mets.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_mets
scrapy crawl mets
sleep 1
cd $mydir/etp_parsing/crawler_mets/crawler_mets/shell_script && \
./docker_stop_mets.sh
