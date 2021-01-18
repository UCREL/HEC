#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=8G
#$ -N cpu-stanza-tagging

source /etc/profile
module add anaconda3/wmlce
source activate $global_scratch/py3.8-gpu-example

bash ./cpu_stanza_tagging.sh $global_scratch/stanza_models