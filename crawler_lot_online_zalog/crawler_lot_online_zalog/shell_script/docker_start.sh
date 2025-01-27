sleep 1
docker run -d -p 8064:8050  --restart=always --cpus=1 -m=1g -c 1024 --name splash_sale_zalog scrapinghub/splash --maxrss 1000  --max-timeout=3600
sleep 1
