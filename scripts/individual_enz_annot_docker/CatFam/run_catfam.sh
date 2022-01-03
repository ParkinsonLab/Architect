# Customize path to BLAST.
PATH=/tools/BLAST_legacy/bin/:$PATH

# Customize path to working directory.
cd /architect_run/organism/CatFam

# Customize path to CatFam.
CATFAM_DIR=/indiv_tools/CatFam
CATFAM_TOOL=${CATFAM_DIR}/source/catsearch.pl
CATFAM_DB=${CATFAM_DIR}/CatFamDB/CatFam_v2.0/CatFam4D99R

COMPLETE_SEQ_NAME=/architect_run/sequence.fa
${CATFAM_TOOL} -d ${CATFAM_DB} -i ${COMPLETE_SEQ_NAME} -o sequence.output 