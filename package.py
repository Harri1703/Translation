from flask import Flask, request, jsonify
from googletrans import Translator
from gtts import gTTS
import os

app = Flask(__name__)
translator = Translator()

# Ensure the 'audio' directory exists
if not os.path.exists('audio'):
    os.makedirs('audio')

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': 'Missing text to translate'}), 400
    
    text = data['text']
    try:
        translated = translator.translate(text, src='en', dest='ta')
        translated_text = translated.text

        # Convert the translated text to speech
        tts = gTTS(text=translated_text, lang='ta')
        audio_file = os.path.join('audio', 'translated_text.mp3')
        tts.save(audio_file)

        return jsonify({'translatedText': translated_text, 'audioFile': audio_file})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
