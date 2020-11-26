#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=4G
#$ -N conda-local

source /etc/profile
module add anaconda3/wmlce

export CONDA_ENVS_PATH=$TMPDIR/.conda/envs
export CONDA_PKGS_DIRS=$TMPDIR/.conda/pkgs

# Assume you always want to install the conda packages to $global_scratch
conda_save_location=$global_scratch/PACKAGE_NAME

# Only timing so that you can lookup in the error log how long it took to install
# 
# --file needs to be changed to the location of the environment.yaml 
# that states what conda needs to install 
time -v conda-env create -p $conda_save_location --file CHANGE-$HOME/environment.yaml

# Changing last modified time, this is done so that it will stay on 
# $global_scratch for the calender month

find $conda_save_location -print | while read filename; do
	touch -h "$filename"
done