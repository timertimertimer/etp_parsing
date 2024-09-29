sleep 1
docker run -d -p 8059:8050  --restart=always --cpus=1 -m=1.5g -c 1024 --name splash_zalog_ross scrapinghub/splash --maxrss 1450  --max-timeout=3600
sleep 1