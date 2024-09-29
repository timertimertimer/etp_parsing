#!/bin/bash
sleep 2
mydir=$HOME
#cache_dir=$mydir/etp_parsing/crawler_be_two_be/.scrapy/

# Category movable_property: equipment, others,  cars
# Category not_movable_property: homes, ground, others, commercial
# Category financial_assets: agreements, material, securities, cesia

sleep 5
cd $mydir/etp_parsing/crawler_lot_online_zalog/crawler_lot_online_zalog/shell_script/ && \
./docker_start.sh
sleep 2
cd $mydir/etp_parsing && \
source env/bin/activate && \
cd $mydir/etp_parsing/crawler_lot_online_zalog
scrapy crawl lot_online_zalog -a category='movable_property' -a subcategory='cars'
sleep 5
scrapy crawl lot_online_zalog -a category='movable_property' -a subcategory='equipment'
sleep 10
scrapy crawl lot_online_zalog -a category='movable_property' -a subcategory='others'
sleep 25

scrapy crawl lot_online_zalog -a category='not_movable_property' -a subcategory='homes'
sleep 10
scrapy crawl lot_online_zalog -a category='not_movable_property' -a subcategory='ground'
sleep 25
scrapy crawl lot_online_zalog -a category='not_movable_property' -a subcategory='others'
sleep 25
scrapy crawl lot_online_zalog -a category='not_movable_property' -a subcategory='commercial'
sleep 25

scrapy crawl lot_online_zalog -a category='financial_assets' -a subcategory='agreements'
sleep 25
scrapy crawl lot_online_zalog -a category='financial_assets' -a subcategory='material'
sleep 25
scrapy crawl lot_online_zalog -a category='financial_assets' -a subcategory='securities'
sleep 25
scrapy crawl lot_online_zalog -a category='financial_assets' -a subcategory='cesia'
sleep 25
cd $mydir/etp_parsing/crawler_lot_online_zalog/crawler_lot_online_zalog/shell_script/ && \
./docker_stop.sh
