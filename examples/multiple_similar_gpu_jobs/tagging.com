#$ -S /bin/bash

#$ -q short
#$ -l ngpus=1
#$ -l ncpus=2
#$ -l h_vmem=8G
#$ -l h_rt=00:05:00
#$ -N multiple-gpu-job
#$ -t 1-2:1

source /etc/profile
module add anaconda3/wmlce
source activate $global_storage/conda_environments/py3.8-multiple-similar-gpu-job

mkdir -p ./output_files
mkdir -p ./output_files/files_$SGE_TASK_ID

for file_number in `seq 0 1`; do
    python tagging.py ./files/files_$SGE_TASK_ID/$file_number.txt ./output_files/files_$SGE_TASK_ID/$file_number.tsv 50 $global_storage/stanza_models
done


