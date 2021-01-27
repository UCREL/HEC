#$ -S /bin/bash

#$ -q serial
#$ -N single-cpu-job

source /etc/profile
module add anaconda3/wmlce
source activate $global_storage/conda_environments/py3.8-single-job

python tagging.py ./alice-in-wonderland.txt ./output.tsv 50