#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=4G
#$ -N conda-local

source /etc/profile
module add anaconda3/wmlce

export CONDA_ENVS_PATH=$global_storage/conda/envs
export CONDA_PKGS_DIRS=$global_storage/conda/pkgs
export PIP_CACHE_DIR=$global_storage/conda/pip

# Assume you always want to install the conda packages to $global_storage
conda_save_location=$global_storage/PACKAGE_NAME

# Only timing so that you can lookup in the error log how long it took to install
# Specify `command time` as want the time executable rather than the built in time
#
# --file needs to be changed to the location of the environment.yaml 
# that states what conda needs to install 
command time -v conda-env create -p $conda_save_location --file ./environment.yaml

if source activate $conda_save_location; then
    command time -v pip install -r conda-requirements.txt
else
    echo "Could not activate the conda environment at $conda_save_location"
fi