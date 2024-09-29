#!/bin/bash
mydir=$HOME
sleep 4
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_nistpru
scrapy crawl nistp
sleep 1
