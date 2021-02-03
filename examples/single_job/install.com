#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=4G
#$ -N conda-install

source /etc/profile
module add anaconda3/wmlce

export CONDA_ENVS_PATH=$global_storage/conda/envs
export CONDA_PKGS_DIRS=$global_storage/conda/pkgs
export PIP_CACHE_DIR=$global_storage/conda/pip

conda_save_location=$global_storage/conda_environments/py3.8-single-job

conda-env create -p $conda_save_location --file ./environment.yaml

if source activate $conda_save_location; then
	python -m spacy download en_core_web_sm
else
    echo "Could not activate the conda environment at $conda_save_location"
fi