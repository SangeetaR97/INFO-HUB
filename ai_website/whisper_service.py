from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import os

app = Flask(__name__)
CORS(app)

print("🔊 Loading Whisper model...")
whisper_model = whisper.load_model("base")
print("✓ Whisper model loaded")

@app.route("/audio-to-text", methods=["POST"])
def audio_to_text():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files["audio"]
    audio_path = "temp_audio.mp3"
    audio.save(audio_path)

    try:
        result = whisper_model.transcribe(audio_path)

        return jsonify({
            "text": result["text"],
            "language": result["language"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

if __name__ == "__main__":
    print("🚀 Whisper Audio-to-Text Service running on http://localhost:6000")
    app.run(debug=True, port=6000)



from flask import Flask, request, send_file
from gtts import gTTS
import uuid, os

app = Flask(__name__)

@app.route("/kannada-tts", methods=["POST"])
def kannada_tts():
    text = request.json["text"]
    filename = f"{uuid.uuid4()}.mp3"

    tts = gTTS(text=text, lang="kn")
    tts.save(filename)

    return send_file(filename, mimetype="audio/mpeg")

if __name__ == "__main__":
    tts = gTTS("ನಮಸ್ಕಾರ, ಇದು ಕನ್ನಡ ಧ್ವನಿ ಪರೀಕ್ಷೆ", lang="kn")
    tts.save("test_kn.mp3")
    print("Kannada MP3 created")
    app.run(debug=True)

