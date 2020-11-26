import argparse
from pathlib import Path

import requests

if __name__ == '__main__':
    
    _help = ('Downloads the GoEmotions dataset. By default this downloads the '
             'dataset that was used to train the model to `./data`.')
    full_help = 'Whether to download the full dataset to `./data/full_dataset`'
    
    parser = argparse.ArgumentParser(description='Downloads the GoEmotions dataset')
    parser.add_argument('--full', action='store_true',
                        help=full_help)
    args = parser.parse_args()

    data_dir = Path(__file__, '..', 'data').resolve()
    if not data_dir.exists():
        data_dir.mkdir()
    
    if args.full:
        data_dir = Path(data_dir, 'full_dataset')
        if not data_dir.exists():
            data_dir.mkdir()
    else:
        base_url = ('https://github.com/google-research/google-research/raw/'
                    'e56477f83f3389390bfb888602bdb71515699378/goemotions/data/')
        splits = ['train', 'dev', 'test']
        for split in splits:
            split_name = f'{split}.tsv'
            split_fp = Path(data_dir, split_name)

            if split_fp.exists():
                continue
            split_url = base_url + f'{split_name}'
            # Very long timeout
            response = requests.get(split_url, timeout=1.0)
            assert response.status_code == requests.codes.ok
            assert response.encoding == 'utf-8'

            with split_fp.open('w') as split_file:
                split_file.write(response.text)