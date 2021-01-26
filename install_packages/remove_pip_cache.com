#$ -S /bin/bash
#$ -q serial
#$ -N remove-pip-cache

source /etc/profile
rm -r $global_storage/conda/pip
