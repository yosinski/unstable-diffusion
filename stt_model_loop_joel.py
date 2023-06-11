#! /usr/bin/env python

# Ignore warnings so demo is cleaner
import warnings
warnings.filterwarnings("ignore")

import time
import sys
import os
import argparse
from IPython import embed
import ipdb as pdb
import whisper
import pyaudio
import wave
import numpy as np
from datetime import datetime

from util import run_cmd
from make_parser import make_parser
from call_model_helper import call_the_model


CHUNK = 1024 * 2
FORMAT = pyaudio.paInt16
NPFORMAT = np.int16
CHANNELS = 1
RATE = 44100
#WAVE_OUTPUT_FILENAME = 'frompy.wav'

# Max readings**2 for a chunck of length 2048
#heuristic_max_power = 11846935
# Float
heuristic_max_power = 826346439192.0
from stt_model_loop import get_text_from_audio


def DEP___get_text_from_audio(args, saveto):
    if args.load_audio is not None:
        audio_filename = args.load_audio
    else:
        # https://stackoverflow.com/questions/40704026/voice-recording-using-pyaudio
        pp = pyaudio.PyAudio()
        stream = pp.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK)

        print("*** recording ***")
        frames = []

        max_power = 0.0
        for ii in range(int(RATE / CHUNK * args.seconds)):
            data = stream.read(CHUNK)
            frames.append(data)
            npdat = np.frombuffer(data, dtype=np.int16).astype(np.float64)
            power = (npdat**2).sum()
            frac = min(1.0, power / heuristic_max_power)
            st = '*' * (1 + int(frac ** .125 * 60))
            #print(f'{ii}: {npdat.sum()}   {sum(data)} {power}')
            #print(f'{ii:02d}: {st}')
            if ii % 1 == 0:
                #print((npdat**2)[:12])
                print(f'{frac:.04f} {st}')
            max_power = max(power, max_power)

        print('Max power was: ', max_power)
        stream.stop_stream()
        stream.close()
        pp.terminate()

        wf = wave.open(saveto, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pp.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f'\nWrote file: {saveto}')

        audio_filename = saveto

    model = whisper.load_model(args.whisper_model)
    result = model.transcribe(audio_filename)
    text = result['text']
    return text


prefixes = [
    'What if instead, you thought: ',
    'Or perhaps: ',
    'Or even: ',
    ]

def main():
    parser = make_parser('Record some audio and convert it to text using the whisper API.')
    args = parser.parse_args()

    while True:
        now = datetime.now()
        datestamp = now.strftime('%y%m%d_%H%M%S')

        if args.enter_to_record:
            print('\nYou:  <enter when ready...>', end='')
            input()
            
        if args.pretend_i_said:
            text = args.pretend_i_said
        else:
            saveto = f'{args.saveto}_{datestamp}.flac'
            text = get_text_from_audio(args, saveto)
        print(f'You: {text}')

        response = call_the_model(args, text)

        #print(f'\nHere is what I have to say to you:\n{response}')

        #short_response = response #.split('.')[0]

        responses = response.split("\n")
        responses = [x for x in responses if len(x)>0]
        responses = [".".join(x.split(".")[1:]).strip() for x in responses]
        responses = [x for x in responses if len(x)>0]
        #responses[1:] = ["Well, actually..." + x for x in responses[1:]]
        responses[1:] = [prefixes[ii] + x for ii, x in enumerate(responses[1:])]

        responses = responses[1:]
        #print(responses)

        voice_rate = args.voice_rate
        #print(f'\nHere is what I have to say to you (short version):\n{short_response}')
        for ii, response in enumerate(responses):
            print(f'\nBot:  {response}')
            if args.speak:
                run_cmd(('say', '-v', 'Daniel', '-r', str(voice_rate), response))
            time.sleep(1)
            voice_rate = int(voice_rate * 1.35)

        if args.embed:
            embed()


if __name__ == '__main__':
    main()
