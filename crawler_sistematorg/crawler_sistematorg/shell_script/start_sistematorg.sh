#!/bin/bash
mydir=$HOME
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_sistematorg
scrapy crawl sistematorg
sleep 1

cd $mydir/etp_parsing/crawler_sistematorg/
dirname=".scrapy"
if [ -d $dirname ]; then
    rm -rf $dirname
fi
