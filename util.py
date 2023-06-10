#! /usr/bin/env python

import os
from datetime import datetime
import subprocess as sp
import requests
import pyaudio


CHUNK_SIZE = 1024


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


def mac_speak(args, text):
    run_cmd(('say', '-v', 'Daniel', '-r', str(args.voice_rate), text))



def play_mp3(filename_mp3):
    '''Playing mp3s requires converting to wav first.'''

    # These seem to work
    FORMAT = pyaudio.paInt16
    RATE = 44100

    assert '.mp3' in filename_mp3, 'Must specify an mp3 filename'

    filename_wav = filename_mp3.replace('.mp3', '.wav')
    #print(f'ffmpeg converting {filename_mp3} to {filename_wav}')
    run_cmd(('ffmpeg', '-y', '-i', filename_mp3, filename_wav))

    file_size = os.stat(filename_wav).st_size

    pp = pyaudio.PyAudio()
    output = pp.open(format=FORMAT,
                     channels=1,
                     rate=RATE,
                     output=True)

    with open(filename_wav, 'rb') as ff:
        while ff.tell() != file_size:
            frame = ff.read(CHUNK_SIZE)
            output.write(frame)


def eleven_speak(args, text):
    assert args.eleven_labs_key is not None, 'Need an Eleven Labs API key'

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
    filename = f'elevenlabs_{datestamp()}.mp3'
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
    print(f'Wrote ElevenLabs file: {filename}')

    play_mp3(filename)
