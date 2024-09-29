sleep 2
docker run -d -p 8049:8050  --restart=always --cpus=1 -m=1.5g -c 1024  --name splash_fabricant scrapinghub/splash --maxrss 1495  --max-timeout=3600 sleep 2
