FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install fastapi uvicorn opencv-python-headless numpy

COPY app.py /app.py

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
