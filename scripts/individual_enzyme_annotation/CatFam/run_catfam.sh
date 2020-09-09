#!/bin/bash
#SBATCH --nodes=1
#SBATCH --time=3:00:00
#SBATCH --job-name=CatFam

# Customize path to BLAST.
PATH=$PATH:${HOME}/blast-2.2.26/bin

# Customize path to working directory.
cd CatFam

# Customize path to CatFam.
CATFAM_DIR=path/to/catfam
CATFAM_TOOL=${CATFAM_DIR}/CatFam/source/catsearch_original.pl
CATFAM_DB=${CATFAM_DIR}/CatFam/CatFamDB/CatFam_v2.0/CatFam4D99R

# Results will be found in folder Results.
mkdir -p Results

# Customize folder name (Split_seqs) with sequences from fasta file split into 40k parts.
for SEQUENCE_FILENAME in `ls Split_seqs`; do
	COMPLETE_SEQ_NAME=Split_seqs/${SEQUENCE_FILENAME};
	${CATFAM_TOOL} -d ${CATFAM_DB} -i ${COMPLETE_SEQ_NAME} -o Results/${SEQUENCE_FILENAME}.output &
done