#! /bin/bash

find $1 -print | while read filename; do
        touch -h "$filename"
done