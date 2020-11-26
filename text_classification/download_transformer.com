#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=4G
#$ -N download-transformer-model

source /etc/profile
module add anaconda3/wmlce

# Activate conda package from where it was saved.
source activate $global_scratch/PACKAGE_NAME

# THIS NEEDS SETTINGS TO WHERE EVER YOU STORE THE TRANSFORMER MODELS
TRANSFORMERS_CACHE=TRANSFORMERS_CACHE
export TRANSFORMERS_CACHE
# Downlaods the bert-base-uncased transformer model to $global_scratch/transformer_models
bash ./transformer_model_download.sh  $global_scratch/transformer_models bert-base-uncased

# Changing last modified time, this is done so that it will stay on 
# $global_scratch for the calender month

find $global_scratch/transformer_models -print | while read filename; do
	touch -h "$filename"
done