import os
import argparse

DEFAULT_RECORD_SECONDS = 3

whisper_model_choices = ['tiny', 'base', 'small', 'medium', 'large']

default_api_key = os.environ.get('OPENAI_API_KEY', None)


def make_parser(descrip=''):
    parser = argparse.ArgumentParser(description=descrip,
                                     formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog)
                                     )


    # Args from call_model
    parser.add_argument(
        '--model', '-m', type=str, default='text-ada-001', help='openai model name')
    parser.add_argument(
        '--prompt_name',
        type=str,
        default='test_prompt',
        help='path to the prompt file')
    parser.add_argument(
        '--test_input_name',
        type=str,
        default='test',
        help='path to the user input file')
    parser.add_argument(
        '--split_start',
        type=str,
        #default='Answer: ',
        default=None,
        help='token indicating start of answer')
    parser.add_argument(
        '--split_end',
        type=str,
        default=None,
        help='token indicating end of answer')
    parser.add_argument(
        '--temperature', type=float, default=0.5, help='temperature')
    parser.add_argument(
        '--max_decoding_steps', type=int, default=128, help='max tokens')
    parser.add_argument(
        '--stop_token',
        type=str,
        default='',
        help='stop decoding on token')
    parser.add_argument(
        '--api_key', type=str, default=default_api_key, help='Openai api key to use. Set here or by exporting the environment variable OPENAI_API_KEY')


    # Args from stt_* scripts
    parser.add_argument('--whisper-model', '-w', type=str, default='base', choices=whisper_model_choices,
                        help='Which Whisper model to use.')
    parser.add_argument('--saveto', '-o', type=str, default='frompy', help='Filename prefix to record to.')
    parser.add_argument('--load-audio', '-l', type=str, default=None, help='Skip recording and use audio loaded from LOAD_AUDIO instead.')
    parser.add_argument('--seconds', '-s', type=float, default=DEFAULT_RECORD_SECONDS, help='How many seconds to record.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Display more information.')
    parser.add_argument('--speak', '-k', action='store_true', help='In addition to printing text to screen, speak it.')
    parser.add_argument('--voice-rate', '-r', type=int, default=175, help='Rate to use for speaking voice')
    parser.add_argument('--embed', '-e', action='store_true', help='Embed in IPython at end.')


    return parser
