#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=4G
#$ -N conda-local

source /etc/profile
module add anaconda3/wmlce

export CONDA_ENVS_PATH=$global_storage/conda/envs
export CONDA_PKGS_DIRS=$global_storage/conda/pkgs
export PIP_CACHE_DIR=$global_storage/conda/pip

conda_save_location=$global_storage/py3.8-gpu-joeynmt

command time -v conda-env create -p $conda_save_location --file ./environment.yaml

if source activate $conda_save_location; then
    command time -v pip install -r conda-requirements.txt
else
    echo "Could not activate the conda environment at $conda_save_location"
fi