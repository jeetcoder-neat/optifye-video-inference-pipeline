import cv2
import time
import json
import base64
from kafka import KafkaProducer

# ======================
# CONFIG
# ======================
RTSP_URL = "rtsp://127.0.0.1:8554/video?tcp"

KAFKA_BROKERS = [
    "b-1.optifyemsk.pzj91d.c2.kafka.ap-south-1.amazonaws.com:9092",
    "b-2.optifyemsk.pzj91d.c2.kafka.ap-south-1.amazonaws.com:9092",
]

TOPIC = "video-stream-1"
BATCH_SIZE = 25
FRAME_SLEEP = 0.03  # ~30 FPS

# ======================
# KAFKA PRODUCER
# ======================
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=5,
    linger_ms=5,
)

# ======================
# RTSP CAPTURE
# ======================
cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
if not cap.isOpened():
    raise RuntimeError("❌ Cannot open RTSP stream")

print("✅ RTSP connected")
print("🚀 RTSP → Kafka producer running")

batch = []
frame_id = 0

while True:
    ret, frame = cap.read()

    if not ret:
        print("⚠️ Frame read failed, retrying...")
        time.sleep(0.5)
        continue

    # Encode frame → JPEG
    frame = cv2.resize(frame, (320, 180))   # MASSIVE size drop
    success, jpeg = cv2.imencode(".jpg", frame,  [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    if not success:
        print("⚠️ JPEG encode failed, skipping frame")
        continue
    
    encoded = base64.b64encode(jpeg.tobytes()).decode("utf-8")

    batch.append({
        "frame_id": frame_id,
        "timestamp": time.time(),
        "image": encoded,
    })

    frame_id += 1

    # Send batch
    if len(batch) == BATCH_SIZE:
        payload = {
            "batch_size": BATCH_SIZE,
            "frames": batch,
        }

        producer.send(TOPIC, payload).get(timeout=10)
        producer.flush()

        print(f"📤 Published batch ending at frame {frame_id}")
        batch = []
        producer.flush()

    time.sleep(FRAME_SLEEP)

