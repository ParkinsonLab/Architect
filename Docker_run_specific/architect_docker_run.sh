PROJECT=organism
OUTPUT_DIR=/architect_run
INPUT_FILE=/tools/Architect/Docker_run_specific/docker_run.in
ARCHITECT=/tools/Architect

python ${ARCHITECT}/architect/set_up_individual_tools.py --arguments_file $INPUT_FILE --project_name $PROJECT --output_dir $OUTPUT_DIR --architect_path $ARCHITECT --i no
python ${ARCHITECT}/architect/run_individual_tools.py --project_name $PROJECT --output_dir $OUTPUT_DIR --i no
python ${ARCHITECT}/architect/format_raw_results.py --project_name $PROJECT --output_dir $OUTPUT_DIR --arguments_file $INPUT_FILE --architect_path $ARCHITECT --i no
python ${ARCHITECT}/architect/run_ensemble_approach.py --arguments_file $INPUT_FILE --project_name $PROJECT --output_dir $OUTPUT_DIR --architect_path $ARCHITECT --i no
#python ${ARCHITECT}/architect/construct_metabolic_model.py --project_name $PROJECT --output_dir $OUTPUT_DIR --arguments_file $INPUT_FILE --project_name $PROJECT --architect_path