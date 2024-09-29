#!/bin/bash
mydir=$HOME
cd $mydir/etp_parsing/crawler_msg_fedresurs/crawler_msg_fedresurs/shell_script && \
./docker_msg_fedres_start.sh
sleep 4
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_msg_fedresurs
scrapy crawl fed_msg_fetch
sleep 20
cd $mydir/etp_parsing/crawler_msg_fedresurs/crawler_msg_fedresurs/shell_script && \
./docker_msg_fedres_stop.sh

#cd $mydir/etp_parsing/crawler_msg_fedresurs/crawler_msg_fedresurs/shell_script && \
#./docker_msg_fedres_start.sh
#cd $mydir/etp_parsing && \
#source env/bin/activate && \
#cd $mydir/etp_parsing/crawler_msg_fedresurs && \
#scrapy crawl fed_msg_fetch_reversed
#cd $mydir/etp_parsing/crawler_msg_fedresurs/crawler_msg_fedresurs/shell_script && \
#./docker_msg_fedres_stop.sh