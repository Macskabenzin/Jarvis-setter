import os
import subprocess
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

# Győződj meg a mikrofon eszköz nevéről ALSA-ban (alapértelmezetten 'Capture' vagy 'Master')
MIXER_CONTROL = os.getenv("MIXER_CONTROL", "Capture")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS Setter - Audio Stream</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #111;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background: #222;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
            text-align: center;
            width: 320px;
        }
        h2 { margin-bottom: 20px; color: #00bcd4; }
        audio { width: 100%; margin-top: 15px; }
        .slider-container { margin-top: 25px; text-align: left; }
        label { display: block; margin-bottom: 8px; font-size: 14px; }
        input[type=range] { width: 100%; cursor: pointer; }
        .vol-val { text-align: right; font-weight: bold; color: #00bcd4; }
    </style>
</head>
<body>

<div class="card">
    <h2>JARVIS Live Stream</h2>
    
    <!-- Audio Lejátszó -->
    <audio id="audioPlayer" controls preload="none">
        <source src="stream" type="audio/mpeg">
        A böngésződ nem támogatja a lejátszást.
    </audio>

    <!-- Mikrofon Hangerő Csúszka -->
    <div class="slider-container">
        <label for="volume">Mikrofon érzékenység / Hangerő:</label>
        <input type="range" id="volume" min="0" max="100" value="80" onchange="updateVolume(this.value)">
        <div class="vol-val"><span id="volNum">80</span>%</div>
    </div>
</div>

<script>
    function updateVolume(val) {
        document.getElementById('volNum').innerText = val;
        fetch('set_volume?level=' + val, { method: 'POST' })
            .catch(err => console.error('Hangerő állítási hiba:', err));
    }
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/stream')
def stream():
    """FFmpeg segítségével közvetíti az ALSA mikrofon hangját MP3 stílusként."""
    cmd = [
        'ffmpeg',
        '-f', 'alsa',
        '-i', 'default',        # Fizikai audio bemenet (ALSA)
        '-acodec', 'libmp3lame',
        '-ab', '128k',
        '-ac', '1',
        '-ar', '44100',
        '-f', 'mp3',
        'pipe:1'
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return Response(process.stdout, mimetype='audio/mpeg')

@app.route('/set_volume', methods=['POST'])
def set_volume():
    """Rendszerszintű ALSA mikrofon hangerő módosítása."""
    level = request.args.get('level', '80')
    try:
        # Beállítja az ALSA bemeneti hangerőt (pl. amixer set Capture 80%)
        subprocess.run(['amixer', 'set', MIXER_CONTROL, f'{level}%'], check=True)
        return {"status": "ok", "level": level}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
