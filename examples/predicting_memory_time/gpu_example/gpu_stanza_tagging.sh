#!/bin/bash

python gpu_stanza_tagging.py ./alice-in-wonderland.txt ./output.tsv 50 $1
python gpu_stanza_tagging.py ./alice-in-wonderland.txt ./output.tsv 300 $1