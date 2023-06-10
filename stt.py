#! /usr/bin/env python

import sys
import os
import argparse
from IPython import embed
import ipdb as pdb
import whisper


whisper_model_choices = ['tiny', 'base', 'small', 'medium', 'large']

def main():
    parser = argparse.ArgumentParser(description='Record some audio and convert it to text using the whisper API.',
                                     formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog)
                                     )
    parser.add_argument('--model', '-m', type=str, default='base', choices=whisper_model_choices,
                        help='Which whisper model to use.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Display more information.')
    parser.add_argument('--embed', '-e', action='store_true', help='Embed in IPython at end.')
    parser.add_argument('audio_file', type=str, help='Which audio file to load')
    args = parser.parse_args()

    model = whisper.load_model(args.model)
    result = model.transcribe(args.audio_file)
    text = result['text']
    print(f'\nHere is what I heard:\n{text}')
    
    if args.embed:
        embed()


if __name__ == '__main__':
    main()
