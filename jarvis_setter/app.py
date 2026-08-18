import subprocess
from flask import Flask, Response, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS Setter</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #121212; 
            color: #fff; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 80vh; 
        }
        .card { 
            background: #1e1e1e; 
            padding: 30px; 
            border-radius: 12px; 
            max-width: 400px; 
            width: 100%; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.6); 
            text-align: center; 
        }
        h2 { color: #00adb5; margin-top: 0; }
        p { color: #aaa; margin-bottom: 25px; }
        audio { width: 100%; outline: none; }
        .live-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background-color: #ff4757;
            border-radius: 50%;
            margin-right: 6px;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.3; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>

<div class="card">
    <h2>JARVIS Setter</h2>
    <p><span class="live-indicator"></span>Élő Stream közvetítés</p>
    
    <!-- Ingress relatív elérés -->
    <audio controls autoplay src="stream_feed"></audio>
</div>

</body>
</html>
"""


def generate_audio_stream():
    """FFmpeg folyamat indítása az ALSA mikrofon hangjának továbbítására"""
    cmd = [
        "ffmpeg",
        "-f",
        "alsa",
        "-i",
        "default",
        "-ac",
        "1",  # Mono
        "-ar",
        "44100",  # 44.1 kHz
        "-b:a",
        "128k",  # 128 kbps MP3
        "-f",
        "mp3",
        "pipe:1",
    ]

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=1024
    )
    try:
        while True:
            data = process.stdout.read(1024)
            if not data:
                break
            yield data
    finally:
        process.kill()


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/stream_feed")
def stream_feed():
    """Szerver oldali MP3 stream végpont"""
    response = Response(generate_audio_stream(), mimetype="audio/mpeg")
    response.headers["Cache-Control"] = (
        "no-cache, no-store, must-revalidate, private"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8097)
