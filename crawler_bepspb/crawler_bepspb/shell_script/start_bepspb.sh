#!/bin/bash
mydir=$HOME
cd $mydir/etp_parsing/crawler_bepspb/crawler_bepspb/shell_script && \
./docker_bepspb_start.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_bepspb
scrapy crawl bepspb
sleep 1
cd $mydir/etp_parsing/crawler_bepspb/crawler_bepspb/shell_script && \
./docker_bepspb_stop.sh

sleep 5
cd $mydir/etp_parsing/crawler_bepspb/crawler_bepspb/shell_script && \
./docker_bepspb_start.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_bepspb
scrapy crawl bepspb_competition
sleep 1
cd $mydir/etp_parsing/crawler_bepspb/crawler_bepspb/shell_script && \
./docker_bepspb_stop.sh

sleep 5
cd $mydir/etp_parsing/crawler_bepspb/crawler_bepspb/shell_script && \
./docker_bepspb_start.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_bepspb
scrapy crawl bepspb_offer
sleep 1
cd $mydir/etp_parsing/crawler_bepspb/crawler_bepspb/shell_script && \
./docker_bepspb_stop.sh