import os
import subprocess
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

# ALSA hangerő szabályzó név (szükség esetén írd át pl. 'Mic'-re vagy 'Master'-re)
MIXER_CONTROL = os.getenv("MIXER_CONTROL", "Capture")

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
            background-color: #1a1a1a;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background: #2d2d2d;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
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
    
    <!-- Élő MP3 Stream -->
    <audio id="audioPlayer" controls preload="none">
        <source src="stream" type="audio/mpeg">
        <source src="stream_feed" type="audio/mpeg">
        A böngésződ nem támogatja a lejátszást.
    </audio>

    <!-- Mikrofon Hangerő Csúszka -->
    <div class="slider-container">
        <label for="volume">Mikrofon érzékenység:</label>
        <input type="range" id="volume" min="0" max="100" value="80" onchange="updateVolume(this.value)">
        <div class="vol-val"><span id="volNum">80</span>%</div>
    </div>
</div>

<script>
    function updateVolume(val) {
        document.getElementById('volNum').innerText = val;
        fetch('set_volume?level=' + val, { method: 'POST' })
            .catch(err => console.error('Hangerő hiba:', err));
    }
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/stream')
@app.route('/stream_feed')
def stream():
    """ALSA bemenet közvetítése MP3 formátumban FFmpeg segítségével."""
    cmd = [
        'ffmpeg',
        '-f', 'alsa',
        '-i', 'default',
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
    """Mikrofon hangerő állítása az ALSA amixer parancsával."""
    level = request.args.get('level', '80')
    try:
        subprocess.run(['amixer', 'set', MIXER_CONTROL, f'{level}%'], check=True)
        return {"status": "ok", "level": level}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    # A portnak pontosan meg kell egyeznie az ingress_port értékével (8097)
    app.run(host='0.0.0.0', port=8097)
