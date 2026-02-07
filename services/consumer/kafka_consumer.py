import json
import base64
import time
import requests
import boto3
import cv2
import numpy as np
from kafka import KafkaConsumer

TOPIC = "video-stream-1"

BROKERS = [
    "b-1.optifyemsk.pzj91d.c2.kafka.ap-south-1.amazonaws.com:9092",
    "b-2.optifyemsk.pzj91d.c2.kafka.ap-south-1.amazonaws.com:9092",
]

# IMPORTANT — we will update this once inference is live
INFERENCE_URL = "http://3.110.80.137:8080/infer"

BUCKET = "optifye-inference-output-382748270280"

s3 = boto3.client("s3")

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BROKERS,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
    group_id="demo-group-live"
)

print("🚀 Consumer started")

for msg in consumer:
    batch = msg.value
    print("Message Received.")

    try:
        response = requests.post(
            INFERENCE_URL,
            json=batch,
            timeout=10
        ).json()

        frame_data = batch["frames"][0]
        boxes = response["results"][0]["boxes"]

        img_bytes = base64.b64decode(frame_data["image"])
        img = cv2.imdecode(
            np.frombuffer(img_bytes, np.uint8),
            cv2.IMREAD_COLOR
        )

        for b in boxes:
            cv2.rectangle(
                img,
                (b["x"], b["y"]),
                (b["x"]+b["w"], b["y"]+b["h"]),
                (0,255,0),
                2
            )

        _, encoded = cv2.imencode(".jpg", img)

        key = f"frame-{int(time.time())}.jpg"

        s3.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=encoded.tobytes(),
            ContentType="image/jpeg"
        )

        print(f"✅ Uploaded {key}")

    except Exception as e:
        print("ERROR:", e)

