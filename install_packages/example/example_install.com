#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=4G
#$ -N conda-local

source /etc/profile
module add anaconda3/wmlce

export CONDA_ENVS_PATH=$TMPDIR/.conda/envs
export CONDA_PKGS_DIRS=$TMPDIR/.conda/pkgs

conda_save_location=$global_scratch/py3.8-gpu-joeynmt

time -v conda-env create -p $conda_save_location --file ./environment.yaml

find $conda_save_location -print | while read filename; do
	touch -h "$filename"
done