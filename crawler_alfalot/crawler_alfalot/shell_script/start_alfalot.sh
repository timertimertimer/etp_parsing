#!/bin/bash
mydir=$HOME
sleep 5
cd $mydir/etp_parsing/crawler_alfalot/crawler_alfalot/shell_script && \
./docker_alflot_start.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_alfalot
scrapy crawl alfalot
sleep 1
cd $mydir/etp_parsing/crawler_alfalot/crawler_alfalot/shell_script && \
./docker_alflot_stop.sh

sleep 20
cd $mydir/etp_parsing/crawler_alfalot/crawler_alfalot/shell_script && \
./docker_alflot_start.sh
sleep 2
cd $mydir/etp_parsing/crawler_alfalot
scrapy crawl alfalot_offer
sleep 1
cd $mydir/etp_parsing/crawler_alfalot/crawler_alfalot/shell_script && \
./docker_alflot_stop.sh

sleep 20
cd $mydir/etp_parsing/crawler_alfalot/crawler_alfalot/shell_script && \
./docker_alflot_start.sh
sleep 2
cd $mydir/etp_parsing/crawler_alfalot
scrapy crawl alfalot_competition
sleep 1
cd $mydir/etp_parsing/crawler_alfalot/crawler_alfalot/shell_script && \
./docker_alflot_stop.sh
