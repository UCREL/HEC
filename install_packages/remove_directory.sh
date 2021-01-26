#!/bin/bash

echo -e "#$ -S /bin/bash\n#$ -q serial\n#$ -N conda-removal\nsource /etc/profile\nrm -r $1" > ./removal.com
qsub ./removal.com
rm ./removal.com