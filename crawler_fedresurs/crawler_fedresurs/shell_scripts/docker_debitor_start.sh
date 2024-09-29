sleep 1
docker run -d -p 8053:8050  --restart=always --cpus=2 -m=3g -c 2048 --name splash_debitor scrapinghub/splash --maxrss 2500  --max-timeout=3600
sleep 1