import argparse
import csv
import logging
from pathlib import Path
from typing import Iterable, List
from resource import getrusage, RUSAGE_SELF
import time
from statistics import median
import sys

import spacy

def file_path(argument_str: str) -> Path:
    '''
    :param argument_str: String from a given argument.
    :returns: Converts argument String to Path type.
    '''
    return Path(argument_str).resolve()

def yield_paragraphs(fp: Path) -> Iterable[str]:
    '''
    Given a file path to a text it will iteratively 
    yield each paragraph within the text until the end of the file.

    A paragraph is defined as continuos block of text. As soon as a blank new 
    line exists a new paragraph is started and the old paragraph is yielded.

    :param fp: File path to a text.
    :returns: Yields paragraphs of text from the file in order from start of 
              file to the end.
    '''
    with fp.open('r') as _file:
        current_paragraph = ''
        for line in _file:
            if line.strip():
                current_paragraph += line
            elif current_paragraph:
                yield current_paragraph
                current_paragraph = ''
        if current_paragraph.strip():
            yield current_paragraph


if __name__ == '__main__':
    program_description = ('Process the text within the given file (1st argument) '
                           'using SpaCy small English NER model and writes all Entities to'
                           'a given TSV file (2nd argument) with the following structure:'
                           '{paragraph_number}\t{entity text}\t{entity label}'
                           '\t{start character offset}\t{end character offset}')
    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('text_file_path', type=file_path, 
                        help='File path to the text to process e.g. Alice in Wonderland.')
    parser.add_argument('output_file_path', type=file_path,
                        help='File path to output the processed data too.')
    parser.add_argument('batch_size', type=int, 
                        help='Number of paragraphs of text for SpaCy to process at a time.')
    args = parser.parse_args()

    text_fp = args.text_file_path
    output_fp = args.output_file_path
    batch_size = args.batch_size

    # Load model
    nlp = spacy.load("en_core_web_sm", disable=[ "tagger", "parser"])
    # Load data
    paragraphs_to_process = yield_paragraphs(text_fp)
    batches_to_process = spacy.util.minibatch(paragraphs_to_process, batch_size)

    # Process data
    paragraph_number = 0
    number_batches = 0
    batch_time: List[float] = []
    with output_fp.open('w+', newline='') as output_file:
        tsv_writer = csv.writer(output_file, delimiter='\t')
        for batch in batches_to_process:
            number_batches += 1
            start_time = time.perf_counter()
            for spacy_doc in nlp.pipe(batch, batch_size=batch_size):
                for entity in spacy_doc.ents:
                        tsv_writer.writerow([paragraph_number, entity.text, 
                                             entity.label_, 
                                             entity.start_char, 
                                             entity.end_char])
                paragraph_number += 1
            end_time = time.perf_counter()
            batch_time.append(end_time - start_time)
    
    # logs to stdout
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    quickest_batch = f'{min(batch_time):0.4f}'
    slowest_batch = f'{max(batch_time):0.4f}'
    median_batch = f'{median(batch_time):0.4f}'
    logger.info(f'Batch times:')
    logger.info(f'Quickest batch: {quickest_batch}')
    logger.info(f'Median: {median_batch}')
    logger.info(f'Slowest: {slowest_batch}')
    
    logger.info(f'Number of batches: {number_batches}')
    
    median_processing_time = median(batch_time) / batch_size
    logger.info(f'Median processing time per sample: {median_processing_time:0.4f}')
    logger.info(f'Total number of samples: {paragraph_number}')
    
    logger.info('Peak amount of memory used: '
                f'{getrusage(RUSAGE_SELF).ru_maxrss / 1000} MB')