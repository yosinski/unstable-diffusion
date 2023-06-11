#! /usr/bin/env python

# Ignore warnings so demo is cleaner
import warnings
warnings.filterwarnings("ignore")

import sys
import os
import argparse
from IPython import embed
import ipdb as pdb
import whisper
import pyaudio
import wave
import numpy as np
from datetime import datetime, timedelta

from util import run_cmd, datestamp, mac_speak, eleven_speak
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


def get_text_from_audio(args, saveto):
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

        if not args.quiet:
            print("*** recording ***")
        frames = []

        max_power = 0.0
        max_frac = 0.0
        ii = 0
        silence_for = 0.0    # How many seconds of silence have occurred
        last_sound = datetime.now()
        sound_threshold = .07           # Level of sound required to have heard anything
        silence_threshold = .03         # Level of sound that counts as silence at end
        silence_time_theshold = timedelta(seconds=1.0)
        heard_something = False
        while True:
            if ii != 0:
                print('\b' * 6, end='')
            st = ('.' * ((ii % 4) + 1)) + (' ' * (5 - (ii % 4)))
            #print(len(st))
            print(st, end='')
            sys.stdout.flush()

            data = stream.read(CHUNK)

            now = datetime.now()
            
            frames.append(data)
            npdat = np.frombuffer(data, dtype=np.int16).astype(np.float64)
            power = (npdat**2).sum()
            frac = min(1.0, power / heuristic_max_power)
            max_frac = max(frac, max_frac)
            heard_something = max_frac > sound_threshold
            silent_now = frac < silence_threshold
            if not silent_now:
                last_sound = now
            silence_for = now - last_sound

            st = '*' * (1 + int(frac ** .125 * 60))
            #print(f'{ii}: {npdat.sum()}   {sum(data)} {power}')
            #print(f'{ii:02d}: {st}')
            if ii % 1 == 0 and not args.quiet:
                #print((npdat**2)[:12])
                print(f'{frac:.04f} {"H" if heard_something else "."}{"s" if silent_now else "."} {st}')
            max_power = max(power, max_power)
            ii += 1

            if args.seconds > 0:
                if ii >= int(RATE / CHUNK * args.seconds):
                    # Finished pre-defined period of recording
                    break
            else:
                #print(frac, silent_now, max_frac, silence_for)
                if heard_something and silence_for > silence_time_theshold:
                    # Auto-detect silence and break
                    if not args.quiet:
                        print('Silent for long enough!')
                    break


        print('\b' * 6, end='')
        st = (' ' * 6)
        print(st, end='')
        sys.stdout.flush()
        #print('\b' * 6, end='')
        #print('\b' * 6)
        #sys.stdout.flush()
        #print('\nhi\n')
        print()
        
        if args.verbose:
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

        if args.verbose:
            print(f'\nWrote file: {saveto}')

        audio_filename = saveto

    model = whisper.load_model(args.whisper_model)
    result = model.transcribe(audio_filename)
    text = result['text']
    return text


def main():
    parser = make_parser('Record some audio and convert it to text using the whisper API.')
    args = parser.parse_args()

    while True:
        dt = datestamp()

        if args.enter_to_record:
            print('\nYou:  <enter when ready...>', end='')
            input()

        if args.pretend_i_said:
            text = args.pretend_i_said
        else:
            saveto = f'{args.saveto}_{dt}.flac'
            text = get_text_from_audio(args, saveto)
        print(f'You: {text}')

        response = call_the_model(args, text)
        short_response = response.split('.')[0]
        print(f'\nBot:  {response}')
        #print(f'\nHere is what I have to say to you (short version):\n{short_response}')
        
        if args.speak:
            if args.use_eleven:
                eleven_speak(args, response)
            else:
                mac_speak(args, response)

        if args.embed:
            embed()


if __name__ == '__main__':
    main()
