import argparse
from pathlib import Path

import requests

def full_path(argument: str) -> Path:
    return Path(argument).resolve()

if __name__ == '__main__':
    
    _help = ('Downloads the GoEmotions dataset. This downloads the '
             'dataset that was used to train the model to the given directory.'
             ' It also downloads the emotions labels `emotions.txt`, as '
             'the emotions in the datasets are represented as line indexes '
             'to the emotions in the `emotions.txt` file.')
    
    parser = argparse.ArgumentParser(description=_help)
    parser.add_argument('data_directory', type=full_path,
                        help='Directory to save the data too.')
    args = parser.parse_args()

    data_dir = args.data_directory
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
    
    base_url = ('https://github.com/google-research/google-research/raw/'
                'e56477f83f3389390bfb888602bdb71515699378/goemotions/data/')
    file_names = ['train.tsv', 'dev.tsv', 'test.tsv', 'emotions.txt']
    for file_name in file_names:
        fp = Path(data_dir, file_name)

        if fp.exists():
            continue
        file_url = base_url + f'{file_name}'
        # Very long timeout
        response = requests.get(file_url, timeout=1.0)
        assert response.status_code == requests.codes.ok
        assert response.encoding == 'utf-8'

        with fp.open('w') as _file:
            _file.write(response.text)
        