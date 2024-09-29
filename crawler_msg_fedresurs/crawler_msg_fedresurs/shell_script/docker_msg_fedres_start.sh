sleep 1
docker run -d -p 8054:8050  --restart=always --cpus=2 -m=3g -c 2048 --name splash_msg_fedres scrapinghub/splash --maxrss 3000  --max-timeout=3600
sleep 5