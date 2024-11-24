from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from gtts import gTTS
from deep_translator import GoogleTranslator

app = Flask(__name__)

# Define language options
languages = {
    "1": {"name": "Hindi", "code": "hi"},
    "2": {"name": "Telugu", "code": "te"},
    "3": {"name": "Kannada", "code": "kn"},
    "4": {"name": "English", "code": "en"}
}

@app.route("/")
def index():
    return render_template("index.html", languages=languages)

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    language_choice = data.get("language_choice")
    if language_choice not in languages:
        return jsonify({"error": "Invalid language choice"}), 400

    selected_language = languages[language_choice]
    
    try:
        # Speech Recognition
        listener = sr.Recognizer()
        with sr.Microphone() as source:
            listener.adjust_for_ambient_noise(source)
            print("Listening...")
            voice = listener.listen(source)
            print("Processing...")

            command = listener.recognize_google(voice, language=selected_language['code'])
            print(f"You said: {command}")

            # Translation
            if selected_language['code'] != "en":
                translation = GoogleTranslator(source=selected_language['code'], target='en').translate(command)
            else:
                translation = command

            # Convert translation to speech
            tts = gTTS(translation, lang='en')
            tts.save("static/translation.mp3")
            return jsonify({ "speech": command,"translation": translation, "audio": "/static/translation.mp3"})

    except sr.UnknownValueError:
        return jsonify({"error": "Google Speech Recognition could not understand the audio. Kindly speak in the language selected."}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Speech Recognition request error: {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
