#!/bin/bash
mydir=$HOME
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_kartoteka_ru
scrapy crawl kartoteka
