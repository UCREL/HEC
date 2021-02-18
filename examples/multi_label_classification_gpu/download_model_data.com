#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=4G
#$ -N download-model-data

source /etc/profile
module add anaconda3/wmlce

source activate $global_storage/conda_environments/py3.7-text-classification

# Download roberta-base
TRANSFORMERS_CACHE=$global_storage/huggingface_transformer_models_cache
export TRANSFORMERS_CACHE
# Downlaods the roberta-base transformer model to $TRANSFORMERS_CACHE
python ./download_transformer_model.py --transformer-model roberta-base

# Download data
python download_data.py $global_storage/data/go-emotions