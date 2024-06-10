from flask import Flask, request, jsonify
import requests
import uuid
import json

app = Flask(__name__)

# Add your key and endpoint
key = "f6bbcf5250f14d3f837b1a339987e6fb"
endpoint = "https://api.cognitive.microsofttranslator.com"
location = "centralindia"

path = '/translate'
constructed_url = endpoint + path

@app.route('/translate', methods=['POST'])
def translate_text():
    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': ['ta']
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4()),
    }

    body = request.json

    response = requests.post(constructed_url, params=params, headers=headers, json=body)
    response_json = response.json()

    return jsonify(response_json)

if __name__ == '__main__':
    app.run(debug=True)
