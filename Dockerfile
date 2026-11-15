# Render image for ONE LETTER. Fonts are not baked in: ser5's DejaVu is mounted read-only.
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pillow==12.2.0 numpy==2.1.3
WORKDIR /work
