#! /usr/bin/env python

import argparse
import os
import pdb
import re
from openai_model import *

from make_parser import make_parser


def main():
    parser = make_parser()
    args = parser.parse_args()
    if args.prompt_name == '':
        prompt_string = ''
    else:
        prompt_string = open(
            os.path.join('prompts', args.prompt_name + '.txt')).read()
        if '\\n' in prompt_string:
            prompt_string = re.sub('\\\\n', '\n', prompt_string)

    if args.test_input_name == '':
        test_input_string = ''
    else:
        test_input_string = open(
            os.path.join('user_inputs', args.test_input_name + '.txt')).read()
        if '\\n' in test_input_string:
            test_input_string = re.sub('\\\\n', '\n', test_input_string)

    model = OpenaiModel(
        args.model, args.api_key, prompt_string=prompt_string)

    model_output = model.call(
        test_example_prompt=test_input_string,
        temperature=args.temperature,
        max_tokens=args.max_decoding_steps,
        stop=args.stop_token)

    extracted_output = model.extract_answer(model_output,
                                            args.split_start,
                                            args.split_end)
    print(extracted_output)
    with open(
            os.path.join('outputs', 'model_response.txt'), 'at') as test_file:
        test_file.write(str(extracted_output) + '\n')


if __name__ == '__main__':
    main()
