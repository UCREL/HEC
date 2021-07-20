#$ -S /bin/bash
#$ -q short
#$ -l ngpus=1
#$ -l ncpus=4
#$ -l h_vmem=40G
#$ -l h_rt=00:25:00
#$ -N run-transformer-model

source /etc/profile
module add anaconda3/wmlce

source activate $global_storage/conda_environments/py3.7-text-classification

TRANSFORMERS_CACHE=$global_storage/huggingface_transformer_models_cache
export TRANSFORMERS_CACHE

DATA_DIR=$global_storage/data/go-emotions/
MODEL_SAVE_DIR=$global_storage/models/go-emotions
mkdir -p $MODEL_SAVE_DIR

python ./bert_model.py ${DATA_DIR}train.tsv ${DATA_DIR}dev.tsv ${DATA_DIR}test.tsv ${DATA_DIR}emotions.txt ${MODEL_SAVE_DIR}/roberta_base.pt --cuda --transformer-model "roberta-base" --batch-size 16