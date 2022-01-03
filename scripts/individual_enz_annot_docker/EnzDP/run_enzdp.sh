# Customize path to EnzDP.
ENZDP_TOOL=/indiv_tools/EnzDP/enzdp.py

project_file=/architect_run/organism/EnzDP/project.py
tmp_folder=/architect_run/organism/EnzDP/tmp

mkdir -p $tmp_folder

python $ENZDP_TOOL ${project_file} ${tmp_folder};
rm -rf ${tmp_folder}