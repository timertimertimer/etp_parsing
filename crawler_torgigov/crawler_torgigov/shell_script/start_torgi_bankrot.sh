#!/bin/bash
mydir=$HOME
sleep 4
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_torgigov
scrapy crawl torgi_bankrot -a section_of_trade='active' 
sleep 1
