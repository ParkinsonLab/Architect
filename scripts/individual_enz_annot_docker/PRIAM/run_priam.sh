# Customize work directory, path to sequences, and priam search jar file.
my_WORKDIR=/architect_run/organism/PRIAM
TEST=/architect_run/organism/sequence.fa
PRIAM_SEARCH=/indiv_tools/PRIAM/PRIAM_search.jar

cd ${my_WORKDIR};

# Customize path to BLAST.
BLAST_BIN=/tools/BLAST_legacy/bin
java -jar ${PRIAM_SEARCH} -n "test" -i $TEST -p /indiv_tools/PRIAM/PRIAM_JAN18 -o "PRIAM_Results" --pt 0 --mp 60 --cc T --bd $BLAST_BIN