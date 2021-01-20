#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=3G
#$ -N multiple-similar-job
#$ -t 1-2:1

source /etc/profile
module add anaconda3/wmlce
source activate $HOME/py3.8-multiple-similar-job

mkdir -p ./output_files
mkdir -p ./output_files/files_$SGE_TASK_ID

for file_number in `seq 0 1`; do
    python tagging.py ./files/files_$SGE_TASK_ID/$file_number.txt ./output_files/files_$SGE_TASK_ID/$file_number.tsv 50 $global_storage/stanza_models
done


