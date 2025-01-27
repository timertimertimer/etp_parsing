sleep 2
docker run -d -p 8055:8050  --restart=always --cpus=1.5 -m=2g -c 2048  --name splash_sber scrapinghub/splash --maxrss 2000  --max-timeout=3600
sleep 2
