#!/bin/bash
sleep 2
mydir=$HOME


sleep 5
cd $mydir/etp_parsing/crawler_akosta/crawler_akosta/shell_script/ && \
./docker_akosta_start.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_akosta
scrapy crawl akosta_new
sleep 1
cd $mydir/etp_parsing/crawler_akosta/crawler_akosta/shell_script/ && \
./docker_akosta_stop.sh

cd $mydir/etp_parsing/crawler_akosta/
filename="data_parse.csv"
if [ -e $filename ]; then
  echo "EXISTS"
#rm -rf "$cache_dir"
fi
