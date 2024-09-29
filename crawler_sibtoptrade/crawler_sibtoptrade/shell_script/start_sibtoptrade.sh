#!/bin/bash
mydir=$HOME
sleep 5
cd $mydir/etp_parsing/crawler_sibtoptrade/crawler_sibtoptrade/shell_script && \
./docker_start_sibtor.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_sibtoptrade
scrapy crawl sibtoptrade

sleep 2
cd $mydir/etp_parsing/crawler_sibtoptrade/
dirname=".scrapy"
if [ -d $dirname ]; then
    rm -rf $dirname
    cd $mydir/etp_parsing/crawler_sibtoptrade/crawler_sibtoptrade/shell_script && \
./docker_stop_sibtor.sh
fi

sleep 1
cd $mydir/etp_parsing/crawler_sibtoptrade/crawler_sibtoptrade/shell_script && \
./docker_stop_sibtor.sh

