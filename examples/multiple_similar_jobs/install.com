#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=4G
#$ -N conda-install

source /etc/profile
module add anaconda3/wmlce

export CONDA_ENVS_PATH=$global_storage/conda/envs
export CONDA_PKGS_DIRS=$global_storage/conda/pkgs
export PIP_CACHE_DIR=$global_storage/conda/pip

conda_save_location=$global_storage/conda_environments/py3.8-multiple-similar-job

conda-env create -p $conda_save_location --file ./environment.yaml

if source activate $conda_save_location; then
    pip install -r conda-requirements.txt
    python ./download_stanza.py $global_storage/stanza_models
else
    echo "Could not activate the conda environment at $conda_save_location"
fi