#$ -S /bin/bash

#$ -q serial
#$ -l h_vmem=2G
#$ -N hf_download

source /etc/profile
module add anaconda3/wmlce
source activate $global_storage/conda_environments/py3.9-hf-hub

mkdir -p $global_storage/hf_models
python hf_download_script.py $global_storage/hf_models/google_electra_small_discriminator google/electra-small-discriminator