#! /usr/bin/env python

import requests
from make_parser import make_parser

CHUNK_SIZE = 1024
#url = "https://api.elevenlabs.io/v1/text-to-speech/<voice-id>"
url_prefix = "https://api.elevenlabs.io/v1/text-to-speech/"

headers = {
  "Accept": "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": "<xi-api-key>"
}

data = {
  "text": "Hi! My name is Bella, nice to meet you!",
  "model_id": "eleven_monolingual_v1",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.5
  }
}

default_voice_id = 'pNInz6obpgDQGcFmaJgB'

def main():
    parser = make_parser('Convert some text to speech using the Eleven Labs API')
    parser.add_argument('text', help='Text to convert to speech')
    args = parser.parse_args()

    headers["xi-api-key"] = args.eleven_labs_key
    data['text'] = args.text
    url = url_prefix + default_voice_id
    
    response = requests.post(url, json=data, headers=headers)
    with open('output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)


if __name__ == '__main__':
    main()
            
