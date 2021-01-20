#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=4G
#$ -N conda-install

source /etc/profile
module add anaconda3/wmlce

export CONDA_ENVS_PATH=$TMPDIR/.conda/envs
export CONDA_PKGS_DIRS=$TMPDIR/.conda/pkgs

conda_save_location=$HOME/py3.8-multiple-similar-job

conda-env create -p $conda_save_location --file ./environment.yaml

source activate $HOME/py3.8-multiple-similar-job
python ./download_stanza.py $global_storage/stanza_models