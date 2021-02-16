#$ -S /bin/bash

#$ -q short
#$ -l ngpus=1
#$ -l ncpus=2
#$ -l h_vmem=8G
#$ -l h_rt=00:10:00
#$ -N gpu-stanza-tagging

source /etc/profile
module add anaconda3/wmlce
source activate $global_storage/conda_environments/py3.8-gpu-example

bash ./gpu_stanza_tagging.sh $global_storage/stanza_models