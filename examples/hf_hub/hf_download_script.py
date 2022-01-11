import argparse
import logging
from pathlib import Path
import sys
from pathlib import Path
from typing import Optional

from huggingface_hub import Repository


def to_path(path_str: str) -> Path:
    return Path(path_str).resolve()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("download_dir", type=to_path, 
                        help="Directory to save the cloned model hub repository too.")
    parser.add_argument("clone_from", type=str,
                        help="Hugging Face model hub repository to clone from.")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        stream=sys.stdout, level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    repository_dir = args.download_dir
    hf_model_hub_repository = args.clone_from
    
    repository: Optional[Repository] = None
    if not repository_dir.is_dir():
        logger.info(f'Cloning {hf_model_hub_repository} to the directory: {repository_dir}')
        repository = Repository(local_dir=repository_dir, clone_from=hf_model_hub_repository, repo_type='model')
    else:
        repository = Repository(local_dir=repository_dir, clone_from=None, repo_type='model')
        logger.info(f'The Hugging Face model hub repository, {hf_model_hub_repository}, '
                    f'has already been cloned too {repository_dir}. Therefore using'
                    ' the already cloned directory.')    
    assert isinstance(repository, Repository)
    print(f'Model card data: {repository.repocard_metadata_load()}')
    print("Files that have been cloned from the "
          f"{hf_model_hub_repository} model repository"
          f" into the directory: {repository_dir}:")
    for file_path in repository_dir.iterdir():
        print(f'{file_path.name}')
    # If you would like to enable uploading of large file >5GB you can run the following:
    repository.lfs_enable_largefiles()