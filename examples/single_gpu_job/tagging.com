#$ -S /bin/bash

#$ -q short
#$ -l ngpus=1
#$ -l ncpus=2
#$ -l h_vmem=8G
#$ -l h_rt=00:05:00
#$ -N single-gpu-job

source /etc/profile
module add anaconda3/wmlce
source activate $global_storage/conda_environments/py3.8-single-job

python tagging.py ./alice-in-wonderland.txt ./output.tsv 50 --gpu