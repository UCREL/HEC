#$ -S /bin/bash
#$ -q serial
#$ -N conda-cache-removal

source /etc/profile
module add anaconda3/wmlce

export CONDA_ENVS_PATH=$global_storage/conda/envs
export CONDA_PKGS_DIRS=$global_storage/conda/pkgs

conda clean -y -a