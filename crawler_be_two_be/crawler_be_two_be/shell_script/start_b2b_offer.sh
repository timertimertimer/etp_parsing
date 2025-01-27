#!/bin/bash
sleep 360
mydir=$HOME
#cache_dir=$mydir/etp_parsing/crawler_be_two_be/.scrapy/

sleep 5
cd $mydir/etp_parsing/crawler_be_two_be/crawler_be_two_be/shell_script/ && \
./docker_b2b_start.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_be_two_be
scrapy crawl betwobe_offer
sleep 1
cd $mydir/etp_parsing/crawler_be_two_be/crawler_be_two_be/shell_script/ && \
./docker_b2b_stop.sh