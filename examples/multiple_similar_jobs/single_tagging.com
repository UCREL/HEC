#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=3G
#$ -N single-multi-file-job

source /etc/profile
module add anaconda3/wmlce
source activate $global_storage/conda_environments/py3.8-multiple-similar-job

mkdir -p ./output_files
for folder_number in `seq 1 2`; do
    mkdir -p ./output_files/files_$folder_number
    for file_number in `seq 0 1`; do
        python tagging.py ./files/files_$folder_number/$file_number.txt ./output_files/files_$folder_number/$file_number.tsv 50 $global_storage/stanza_models
    done
done


