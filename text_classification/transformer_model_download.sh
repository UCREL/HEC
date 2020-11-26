#! /bin/bash

TRANSFORMERS_CACHE=$1
export TRANSFORMERS_CACHE
python ./download_transformer_model.py --transformer-model $2