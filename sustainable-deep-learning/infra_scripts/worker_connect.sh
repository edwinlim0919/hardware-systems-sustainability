#!/bin/bash
export PATH="$HOME/miniconda3/bin:$PATH"
export PATH='/users/'"${USER}"'/miniconda3/envs/intel-transformers/bin:'"$PATH"
conda init
conda activate intel-transformers
ray start --address='130.127.133.221:6379'