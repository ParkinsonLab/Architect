EFICAz25_PATH=/indiv_tools/EFICAz2.5.1
export EFICAz25_PATH

cd /architect_run/organism/EFICAz

cp ../../sequence.fa sequence.fa

python $EFICAz25_PATH/bin/EFICAz_latest.py sequence.fa > output.out