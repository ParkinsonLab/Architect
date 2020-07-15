#!/bin/bash
#SBATCH --nodes=1
#SBATCH --time=3:00:00
#SBATCH --job-name=PRIAM

# Customize work directory, path to sequences, and priam search jar file.
my_WORKDIR=PRIAM
TEST=sequences.fa
PRIAM_SEARCH=$HOME/PRIAM/PRIAM_search_2018.jar

module load java;
module load gcc;
module load lmdb;
module load boost;
module load gmp;
module load blast+;

cd ${my_WORKDIR};

# Customize path to BLAST.
BLAST_BIN=${HOME}/blast-2.2.26/bin
java -jar ${PRIAM_SEARCH} -n "test" -i $TEST -p ${HOME}/Enzyme_Annotation/PRIAM/PRIAM_JAN18 -o "PRIAM_Results" --pt 0 --mp 60 --cc T --bd $BLAST_BIN --np 40
