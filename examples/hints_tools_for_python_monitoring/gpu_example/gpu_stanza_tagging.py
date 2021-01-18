import argparse
import csv
import logging
from pathlib import Path
from typing import Iterable, List
from resource import getrusage, RUSAGE_SELF
import time
import sys

import stanza
from stanza_batch import batch
from pynvml import nvmlShutdown, nvmlInit
from pynvml import nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo



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
    with fp.open('r', encoding='utf-8-sig') as _file:
        current_paragraph = ''
        for line in _file:
            if line.strip():
                current_paragraph += line
            elif current_paragraph:
                yield current_paragraph
                current_paragraph = ''
        if current_paragraph.strip():
            yield current_paragraph

def bytes_to_GB(number_bytes: int) -> int:
    return number_bytes / (1024**3)



if __name__ == '__main__':
    program_description = ('Process the text within the given file (1st argument) '
                           'using Stanza English NER model and writes all Entities to'
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
    parser.add_argument('stanza_model_directory', type=file_path, 
                        help='Directory to store the pre-trained stanza models.')
    args = parser.parse_args()

    # Allows us to sample statistics from the nvidia GPU
    nvmlInit()
    # Assuming we only have access to one GPU
    gpu_handle = nvmlDeviceGetHandleByIndex(0)
    gpu_info = nvmlDeviceGetMemoryInfo(gpu_handle)
    gpu_memory_start = bytes_to_GB(gpu_info.used)

    
    
    

    text_fp = args.text_file_path
    output_fp = args.output_file_path
    batch_size = args.batch_size
    stanza_model_directory = args.stanza_model_directory
    stanza_model_directory.mkdir(exist_ok=True)

    # Download the relevant stanza model if it has not already been downloaded.
    stanza_processes = 'tokenize,ner'
    stanza.download("en", dir=str(stanza_model_directory), 
                    processors=stanza_processes)
    # load the stanza model
    nlp = stanza.Pipeline(lang='en', processors=stanza_processes, use_gpu=True,
                          tokenize_batch_size=batch_size,
                          ner_batch_size=batch_size, 
                          dir=str(stanza_model_directory))

    # GPU memory used for loading model
    gpu_info = nvmlDeviceGetMemoryInfo(gpu_handle)
    gpu_memory_before_processing = bytes_to_GB(gpu_info.used)
    gpu_memory_for_model = gpu_memory_before_processing - gpu_memory_start
    
    
    # Load data
    paragraphs_to_process = yield_paragraphs(text_fp)

    # Process data
    paragraph_number = 0
    processing_time: float = 0.0
    gpu_memory_used_during_processing: List[int] = []
    with output_fp.open('w+', newline='') as output_file:
        tsv_writer = csv.writer(output_file, delimiter='\t')
        start_time = time.perf_counter()
        for stanza_document in batch(paragraphs_to_process, nlp, batch_size=batch_size):
            for entity in stanza_document.ents:
                tsv_writer.writerow([paragraph_number, entity.text, 
                                     entity.type, 
                                     entity.start_char, 
                                     entity.end_char])
            paragraph_number += 1
            # Only sample the amount of memory used every N (N=50 in this case)
            # documents. The more we sample the better we map the amount 
            # of GPU memory being used, but can take longer especially with lots 
            # of documents/paragraphs. 
            if paragraph_number % 50 == 0:
                gpu_info = nvmlDeviceGetMemoryInfo(gpu_handle)
                gpu_memory_used = bytes_to_GB(gpu_info.used) - gpu_memory_before_processing
                gpu_memory_used_during_processing.append(gpu_memory_used)

        end_time = time.perf_counter()
        processing_time = end_time - start_time
    
    
    # logs to stdout
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    logger.info(f'Total time: {processing_time:.4f}s')

    mean_batch_time = (processing_time / paragraph_number) * batch_size
    logger.info(f'Mean batch time for batch size {batch_size}: {mean_batch_time:.4f}s')
    logger.info(f'Total number of samples: {paragraph_number}')

    logger.info(f"Total GPU memory: {bytes_to_GB(gpu_info.total):.4f}GB")
    logger.info(f"Amount of GPU memory used before running script: {gpu_memory_start:.4f}GB")
    logger.info(f"GPU memory used for loading model: {gpu_memory_for_model:.4f}GB")

    logger.info('Peak GPU memory used for processing batch '
                f'{max(gpu_memory_used_during_processing):.4f}GB')
    peak_gpu_memory = gpu_memory_before_processing + max(gpu_memory_used_during_processing)
    peak_gpu_memory = peak_gpu_memory - gpu_memory_start
    logger.info(f'Peak GPU memory used {peak_gpu_memory:.4f}GB')

    # Amount of RAM being used before script. (1024**2) converts it to GB from KB
    ram_memory_end = getrusage(RUSAGE_SELF).ru_maxrss / (1024**2)
    logger.info(f'Peak RAM memory used {ram_memory_end:.4f}GB')
    nvmlShutdown()