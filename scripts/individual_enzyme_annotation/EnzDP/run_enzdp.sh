#!/bin/bash
#SBATCH --nodes=1
#SBATCH --time=3:00:00
#SBATCH --job-name=EnzDP 

# Customize path to EnzDP.
ENZDP_TOOL=${HOME}/EnzDP/EnzDP_src/enzdp.py

# Specify full path to working directory (containing Project folder; see README), and path to a folder which can contain many files.
# (EnzDP generates many intermediate files, which may occupy space that the user does not have enough of.)
folder=EnzDP
local_path=/dev/EnzDP

mkdir -p ${local_path}

for file in `ls ${folder}/Project/*`; do
	(just_file=$(basename $file); 
	just_file_2=$(echo $just_file | sed "s|\.|_|g"); 
	mkdir -p ${local_path}/${just_file_2}; 
	python $ENZDP_TOOL ${file} ${local_path}/${just_file_2}; 
	rm -rf ${local_path}/${just_file_2}) &
done
