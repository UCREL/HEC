#!/bin/bash

mkdir -p ./scalene_output
scalene --outfile ./scalene_output/scalene_50.txt  tagging.py alice-in-wonderland.txt output.tsv 50
scalene --outfile ./scalene_output/scalene_300.txt  tagging.py alice-in-wonderland.txt output.tsv 300

scalene --outfile ./scalene_output/scalene_reduced_50.txt  --reduced-profile tagging.py alice-in-wonderland.txt output.tsv 50
scalene --outfile ./scalene_output/scalene_reduced_300.txt  --reduced-profile tagging.py alice-in-wonderland.txt output.tsv 300