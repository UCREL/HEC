import argparse
from pathlib import Path

import stanza

def file_path(argument_str: str) -> Path:
    '''
    :param argument_str: String from a given argument.
    :returns: Converts argument String to Path type.
    '''
    return Path(argument_str).resolve()

if __name__ == '__main__':
    program_description = ('Downloads the stanza tokenizer and NER model to '
                           'the directory given in the first argument.')
    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('stanza_model_directory', type=file_path, 
                        help='Directory to store the pre-trained stanza models.')
    args = parser.parse_args()

    stanza_processes = 'tokenize,ner'
    stanza.download("en", dir=str(args.stanza_model_directory), 
                    processors=stanza_processes)