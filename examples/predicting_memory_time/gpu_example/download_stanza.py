import argparse
import logging
from pathlib import Path
from resource import getrusage, RUSAGE_SELF
import sys

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

    # logs to stdout
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    # Amount of RAM being used before script. (1024**2) converts it to GB from KB
    ram_memory_end = getrusage(RUSAGE_SELF).ru_maxrss / (1024**2)
    logger.info(f'Peak RAM memory used {ram_memory_end:.4f}GB')