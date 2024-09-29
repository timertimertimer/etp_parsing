sleep 1
docker run -d -p 8057:8050  --restart=always --cpus=1 -m=1.5g -c 1024 --name splash_b2b scrapinghub/splash --maxrss 1495  --max-timeout=3600
sleep 1