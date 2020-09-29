#!/bin/bash
#SBATCH --nodes=1
#SBATCH --time=12:00:00
#SBATCH --job-name=DETECT

# Customize path to DETECT.
DETECT_TOOL=${HOME}/DETECTv2/detect_2.2.7.py

# Customize path to EMBOSS, and DETECT directory.
export PATH=${HOME}/DETECTv2/:$PATH
export PATH=path/to/EMBOSS/EMBOSS-6.6.0/emboss/:$PATH

module load NiaEnv/2018a;
module load gcc;
module load lmdb;
module load boost;
module load gmp;
module load blast+;
module load anaconda3;

# Go to directory with sequences
cd DETECT

DUMP_DIR=$PWD/dump
mkdir -p $DUMP_DIR

# Customize sequence file name.
SEQ_NAME=sequences.fa

python $DETECT_TOOL ${SEQ_NAME} --output_file output_40.out --dump_dir $DUMP_DIR --n_count 40