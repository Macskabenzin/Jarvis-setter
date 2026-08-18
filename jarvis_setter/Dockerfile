FROM python:3.11-slim

# FFmpeg és ALSA eszközök telepítése a streameléshez
RUN apt-get update && apt-get install -y \
    ffmpeg \
    alsa-utils \
    pulseaudio-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8097

CMD ["python", "app.py"]
