#! /usr/bin/env python

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


whisper_model_choices = ['tiny', 'base', 'small', 'medium', 'large']

CHUNK = 1024 * 2
FORMAT = pyaudio.paInt16
NPFORMAT = np.int16
CHANNELS = 1
RATE = 44100
DEFAULT_RECORD_SECONDS = 3
#WAVE_OUTPUT_FILENAME = 'frompy.wav'

# Max readings**2 for a chunck of length 2048
#heuristic_max_power = 11846935
# Float
heuristic_max_power = 826346439192.0


def main():
    parser = argparse.ArgumentParser(description='Record some audio and convert it to text using the whisper API.',
                                     formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog)
                                     )
    parser.add_argument('--model', '-m', type=str, default='base', choices=whisper_model_choices,
                        help='Which whisper model to use.')
    parser.add_argument('--saveto', '-o', type=str, default='frompy', help='Filename prefix to record to.')
    parser.add_argument('--load_audio', '-l', type=str, default=None, help='Skip recording and use audio loaded from LOAD_AUDIO instead.')
    parser.add_argument('--seconds', '-s', type=float, default=DEFAULT_RECORD_SECONDS, help='How many seconds to record.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Display more information.')
    parser.add_argument('--embed', '-e', action='store_true', help='Embed in IPython at end.')
    args = parser.parse_args()

    now = datetime.now()
    datestamp = now.strftime('%y%m%d_%H%M%S')

    saveto = f'{args.saveto}_{datestamp}.flac'

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
            if ii % 2 == 0:
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

    model = whisper.load_model(args.model)
    result = model.transcribe(audio_filename)
    text = result['text']
    print(f'\nHere is what I heard:\n{text}')
    
    if args.embed:
        embed()


if __name__ == '__main__':
    main()
