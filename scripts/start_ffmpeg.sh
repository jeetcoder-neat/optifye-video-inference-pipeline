#!/bin/bash

VIDEO_PATH="/home/ec2-user/video.mp4"

echo "Starting FFmpeg stream..."

ffmpeg -re -stream_loop -1 \
-i $VIDEO_PATH \
-rtsp_transport tcp \
-c copy \
-f rtsp rtsp://localhost:8554/video
