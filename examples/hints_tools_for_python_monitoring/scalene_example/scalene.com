#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=2G
#$ -N scalene

source /etc/profile
module add anaconda3/wmlce
source activate $global_scratch/py3.8-scalene

bash ./scalene.sh