from flask import Flask, request, jsonify, send_file
import requests
import uuid
import os
from gtts import gTTS
import base64

app = Flask(__name__)

# Add your key and endpoint
key = "f6bbcf5250f14d3f837b1a339987e6fb"
endpoint = "https://api.cognitive.microsofttranslator.com"
location = "centralindia"

path = '/translate'
constructed_url = endpoint + path

# Ensure the 'audio' folder exists
if not os.path.exists('audio'):
    os.makedirs('audio')

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json
    text_to_translate = data['text']
    target_languages = data.get('languages', ['ta'])  # Default to Tamil if no languages are specified

    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': target_languages
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4()),
    }

    body = [{'text': text_to_translate}]

    response = requests.post(constructed_url, params=params, headers=headers, json=body)
    response_json = response.json()

    translations = []

    for translation in response_json[0]['translations']:
        lang = translation['to']
        translated_text = translation['text']

        # Convert the translated text to speech
        tts = gTTS(text=translated_text, lang=lang)
        audio_file_name = f"{uuid.uuid4()}.mp3"
        audio_file_path = os.path.join('audio', audio_file_name)
        tts.save(audio_file_path)

        # Read the audio file and encode it to Base64
        with open(audio_file_path, "rb") as audio_file:
            encoded_audio = base64.b64encode(audio_file.read()).decode('utf-8')

        translations.append({
            'language': lang,
            'translated_text': translated_text,
            'audio_file': audio_file_name,
            'audio_content': encoded_audio
        })

    return jsonify(translations)

if __name__ == '__main__':
    app.run(debug=True)
