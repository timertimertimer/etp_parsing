sleep 1
docker run -d -p 8069:8050  --restart=always --cpus=1 -m=1g -c 1024 --name splash_mets scrapinghub/splash --maxrss 1024  --max-timeout=3600
sleep 1