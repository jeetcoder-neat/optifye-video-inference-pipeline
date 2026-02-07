#!/bin/bash

echo "Stopping any existing RTSP container..."

docker stop mediamtx 2>/dev/null || true
docker rm mediamtx 2>/dev/null || true

echo "Starting MediaMTX RTSP server..."

docker run --rm -it \
--name mediamtx \
-p 8554:8554 \
-v /home/ec2-user/mediamtx.yml:/mediamtx.yml \
bluenviron/mediamtx
