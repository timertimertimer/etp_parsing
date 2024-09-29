#!/bin/bash
mydir=$HOME
cd $mydir/etp_parsing/crawler_sales_lot_online/crawler_sales_lot_online/shell_script && \
./docker_lot_online_start.sh
sleep 4
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_sales_lot_online
scrapy crawl lot_online_ru
sleep 1
cd $mydir/etp_parsing/crawler_sales_lot_online/crawler_sales_lot_online/shell_script && \
./docker_lot_online_stop.sh