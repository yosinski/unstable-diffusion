#! /usr/bin/env python

from datetime import datetime
import subprocess as sp


def run_cmd(cmd_tuple, check=False, concat_stderr=False):
    proc = sp.run(cmd_tuple, capture_output=True, check=check)
    #out, err = proc.communicate()
    out = proc.stdout.strip().decode()
    if concat_stderr:
        err = proc.stderr.strip().decode()
        if len(err) > 0:
            out += '\n' + err
    return out


def datestamp():
    now = datetime.now()
    datestamp = now.strftime('%y%m%d_%H%M%S')
    return datestamp


def eleven_labs_doit(args, text):
    assert args.eleven_labs_key is not None, 'Need an Eleven Labs API key'
    
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

    default_voice_id = 'pNInz6obpgDQGcFmaJgB'   # Adam

    headers["xi-api-key"] = args.eleven_labs_key
    data['text'] = text
    url = url_prefix + default_voice_id
    
    response = requests.post(url, json=data, headers=headers)
    with open('output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

