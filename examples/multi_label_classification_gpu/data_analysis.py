import csv
from pathlib import Path
from typing import Dict, List
from collections import Counter

DATA_DIR = Path(__file__, '..', 'data').resolve()
if not DATA_DIR.exists():
    raise FileNotFoundError(f'The directory that stores that data: {DATA_DIR} '
                            ' does not exist when it should. Please download '
                            'the GoEmotions data.')

def label_statistics(split_fp: Path) -> str:
    '''
    :param split_fp: A TSV file path containing the GoEmotions data. columns:
                     1. text, 2. comma separated list of label ids, 3. ID of 
                     data.
    :returns: A string where on each line contains the following separated by 
              a comma: 1. label name, 2. label raw count, 3. percentage of 
              texts that contains this label, and 4. percentage of times it 
              occurs with another label. The final line states that total number
              of texts.
    '''
    label_name_fp = Path(DATA_DIR, 'emotions.txt')
    label_name_mapper: Dict[int, str] = {}
    label_order: List[int] = []

    with label_name_fp.open('r') as label_name_file:
        for index, line in enumerate(label_name_file):
            label_name_mapper[index] = line.strip()
            label_order.append(index)
    
    text_count = 0
    label_counter = Counter()
    multiple_labels_counter = Counter()
    with split_fp.open('r', newline='') as data_file:
        tsv_reader = csv.reader(data_file, delimiter='\t')
        for line in tsv_reader:
            text = line[0].strip()
            labels = line[1].split(',')
            if not labels:
                raise ValueError('There should always be a label assigned to '
                                 f'a text: {line}')
            labels = [int(label) for label in labels]
            label_counter.update(labels)
            if len(labels) > 1:
                multiple_labels_counter.update(labels)
            text_count += 1
    assert len(label_counter) == 28, f'Not all labels exist in this file {split_fp}'
    
    label_string = ''
    for label_id in label_order:
        label_name = label_name_mapper[label_id]
        raw_count = label_counter[label_id]
        percentage_count = (float(raw_count) / text_count) * 100
        multi_percentage = 0.0
        if label_id in multiple_labels_counter:
            multi_raw_count = multiple_labels_counter[label_id]
            multi_percentage = ( multi_raw_count / float(raw_count)) * 100
        label_string += (f'{label_name}, {raw_count}, '
                         f'{percentage_count:.2f}%, {multi_percentage:.2f}% \n')
    label_string += f'Text count: {text_count}'
    return label_string


if __name__ == '__main__':
    split_names = ['train', 'dev', 'test']
    for split_name in split_names:
        split_fp = Path(DATA_DIR, f'{split_name}.tsv')
        
        print(f'{split_name} label statistics:\n')
        print(label_statistics(split_fp))
        print('\n\n')