#$ -S /bin/bash
#$ -q gpu
#$ -l ngpus=1
#$ -l ncpus=4
#$ -l h_vmem=40G
#$ -l h_rt=00:25:00
#$ -N run-transformer-model

source /etc/profile
module add anaconda3/wmlce

# Activate conda package from where it was saved.
source activate $global_scratch/PACKAGE_NAME

python ./bert_model.py ./data/train.tsv ./data/dev.tsv ./data/test.tsv ./data/emotions.txt ./models/saved_model.pt --cuda --batch-size 16