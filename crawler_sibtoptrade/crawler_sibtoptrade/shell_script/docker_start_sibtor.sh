sleep 1
docker run -d -p 8065:8050  --restart=always --cpus=1 -m=1g -c 1024 --name splash_sibtoptrade scrapinghub/splash --maxrss 1000  --max-timeout=3600
sleep 1