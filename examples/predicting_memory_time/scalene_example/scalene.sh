#!/bin/bash

mkdir ./scalene_output
scalene --outfile ./scalene_output/scalene_50.html --html tagging.py alice-in-wonderland.txt output.tsv 50
scalene --outfile ./scalene_output/scalene_300.html --html tagging.py alice-in-wonderland.txt output.tsv 300

scalene --outfile ./scalene_output/scalene_reduced_50.html --html --reduced-profile tagging.py alice-in-wonderland.txt output.tsv 50
scalene --outfile ./scalene_output/scalene_reduced_300.html --html --reduced-profile tagging.py alice-in-wonderland.txt output.tsv 300