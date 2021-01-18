#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=4G
#$ -N conda-install

source /etc/profile
module add anaconda3/wmlce

export CONDA_ENVS_PATH=$TMPDIR/.conda/envs
export CONDA_PKGS_DIRS=$TMPDIR/.conda/pkgs

conda_save_location=$global_scratch/py3.8-scalene

conda-env create -p $conda_save_location --file ./environment.yaml

source activate $global_scratch/py3.8-scalene
python -m spacy download en_core_web_sm

find $conda_save_location -print | while read filename; do
	touch -h "$filename"
done