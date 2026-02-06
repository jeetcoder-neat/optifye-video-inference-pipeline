from fastapi import FastAPI
import cv2
import base64
import numpy as np

app = FastAPI()

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

@app.post("/infer")
def infer(payload: dict):
    results = []

    for frame in payload["frames"]:
        img_bytes = base64.b64decode(frame["image"])
        img = cv2.imdecode(
            np.frombuffer(img_bytes, np.uint8),
            cv2.IMREAD_COLOR
        )

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        boxes = []
        for (x, y, w, h) in faces:
            boxes.append({
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h)
            })

        results.append({
            "frame_id": frame["frame_id"],
            "boxes": boxes
        })

    return {"results": results}
