# Customize path to DETECT.
DETECT_TOOL=/indiv_tools/DETECTv2/detect.py

# Customize path to EMBOSS, and DETECT directory.
export PATH=/indiv_tools/DETECTv2/:$PATH
export PATH=/tools/EMBOSS-6.6.0/emboss/:$PATH
export PATH=/tools/BLAST_plus/bin/:$PATH

cd /architect_run/organism/DETECT

# Customize sequence file name.
SEQ_NAME=/architect_run/sequence.fa

python $DETECT_TOOL ${SEQ_NAME} --output_file output_40.out