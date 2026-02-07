from fastapi import FastAPI
import cv2
import base64
import numpy as np

app = FastAPI()


@app.post("/infer")
def infer(payload: dict):
    results = []

    frames = payload.get("frames", [])

    # We draw rectangle ONLY on the first valid frame
    rectangle_drawn = False

    for frame in frames:

        img_bytes = base64.b64decode(frame["image"])

        img = cv2.imdecode(
            np.frombuffer(img_bytes, np.uint8),
            cv2.IMREAD_COLOR
        )

        # Crash protection (VERY important)
        if img is None:
            continue

        boxes = []

        # Draw rectangle ONLY once per batch
        if not rectangle_drawn:
            h, w, _ = img.shape

            x1 = int(w * 0.25)
            y1 = int(h * 0.25)
            x2 = int(w * 0.75)
            y2 = int(h * 0.75)

            cv2.rectangle(
                img,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),   # bright green
                4              # thick so it's visible in S3
            )

            boxes.append({
                "x": x1,
                "y": y1,
                "w": x2 - x1,
                "h": y2 - y1
            })

            rectangle_drawn = True

        # Encode annotated frame
        _, buffer = cv2.imencode(".jpg", img)

        encoded_img = base64.b64encode(buffer).decode("utf-8")

        results.append({
            "frame_id": frame["frame_id"],
            "boxes": boxes,
            "image": encoded_img
        })

    return {"results": results}
