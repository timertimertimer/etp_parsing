#!/bin/bash
mydir=$HOME
cd $mydir/etp_parsing/crawler_aistorg/crawler_aistorg/shell_script && \
./docker_start_aitorg.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_aistorg && \
scrapy crawl aistorg
sleep 1
cd $mydir/etp_parsing/crawler_aistorg/crawler_aistorg/shell_script && \
./docker_stop_aistorg.sh
