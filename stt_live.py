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


whisper_model_choices = ['tiny', 'base', 'small', 'medium', 'large']

CHUNK = 1024 * 2
FORMAT = pyaudio.paInt16
NPFORMAT = np.int16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 3
#WAVE_OUTPUT_FILENAME = 'frompy.wav'

# Max readings**2 for a chunck of length 2048
heuristic_max_power = 11846935


def main():
    parser = argparse.ArgumentParser(description='Record some audio and convert it to text using the whisper API.',
                                     formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog)
                                     )
    parser.add_argument('--model', '-m', type=str, default='base', choices=whisper_model_choices,
                        help='Which whisper model to use.')
    parser.add_argument('--saveto', '-o', type=str, default='frompy.wav', help='Filename to write audio to.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Display more information.')
    parser.add_argument('--embed', '-e', action='store_true', help='Embed in IPython at end.')
    args = parser.parse_args()

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
    for ii in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        npdat = np.frombuffer(data, dtype=np.int16)
        power = (npdat**2).sum()
        frac = min(1.0, power / heuristic_max_power)
        st = '*' * int(frac**2 * 40)
        #print(f'{ii}: {npdat.sum()}   {sum(data)} {power}')
        #print(f'{ii:02d}: {st}')
        if ii % 2 == 0:
            print(f'{st}')
        max_power = max(power, max_power)

    stream.stop_stream()
    stream.close()
    pp.terminate()

    wf = wave.open(args.saveto, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pp.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f'\nWrote file: {args.saveto}')

    model = whisper.load_model(args.model)
    result = model.transcribe(args.saveto)
    text = result['text']
    print(f'\nHere is what I heard:\n{text}')
    
    if args.embed:
        embed()


if __name__ == '__main__':
    main()
