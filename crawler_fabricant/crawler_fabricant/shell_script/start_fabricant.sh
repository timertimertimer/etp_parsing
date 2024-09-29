#!/bin/bash
mydir=$HOME
cd $mydir/etp_parsing/crawler_fabricant/crawler_fabricant/shell_script && \
./docker_fabricant_start.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_fabricant
scrapy crawl fabricant
sleep 1
cd $mydir/etp_parsing/crawler_fabricant/crawler_fabricant/shell_script && \
./docker_fabricant_stop.sh

cd $mydir/etp_parsing/crawler_fabricant/
dirname=".scrapy"
if [ -d $dirname ]; then
    rm -rf $dirname
fi