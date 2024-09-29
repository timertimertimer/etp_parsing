#!/bin/bash
mydir=$HOME
sleep 4
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_tenderstandartru &&\
scrapy crawl tenderstandartru
sleep 1

cd $mydir/etp_parsing/crawler_tenderstandartru/
dirname=".scrapy"
if [ -d $dirname ]; then
    rm -rf $dirname
fi