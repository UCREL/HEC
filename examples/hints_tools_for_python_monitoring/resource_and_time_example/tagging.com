#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=2G
#$ -N tagging

source /etc/profile
module add anaconda3/wmlce
source activate $global_storage/conda_environments/py3.8-resource-time

bash ./tagging.sh