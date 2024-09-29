#!/bin/bash
mydir=$HOME
sleep 4
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_promkonsalt
scrapy crawl promkonsalt
sleep 1