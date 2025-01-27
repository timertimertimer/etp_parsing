#!/bin/bash
sleep 2
mydir=$HOME
cd $mydir/etp_parsing
source env/bin/activate
cd $mydir/etp_parsing/crawler_altimeta
scrapy crawl trade_place_vetp_tu