#!/bin/bash
mydir=$HOME
sleep 4
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_rutrade24
scrapy crawl ruTrade24
sleep 1

cd $mydir/etp_parsing/crawler_rutrade24/
dirname=".scrapy"
if [ -d $dirname ]; then
    rm -rf $dirname
fi
sleep 1
cd $mydir/etp_parsing/crawler_rutrade24/
filename="items.json"
if [ -e $filename ]; then
    rm -rf $filename
fi