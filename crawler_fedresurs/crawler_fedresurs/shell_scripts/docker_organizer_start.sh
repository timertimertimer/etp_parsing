sleep 1
docker run -d -p 8052:8050  --restart=always --cpus=2 -m=2.5g -c 2048 --name splash_org scrapinghub/splash --maxrss 2500  --max-timeout=3600
sleep 1