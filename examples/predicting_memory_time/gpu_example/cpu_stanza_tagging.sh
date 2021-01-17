#!/bin/bash

python cpu_stanza_tagging.py ./alice-in-wonderland.txt ./output.tsv 50 $1
python cpu_stanza_tagging.py ./alice-in-wonderland.txt ./output.tsv 300 $1