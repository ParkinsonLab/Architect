PATH=/cygdrive/c/Users/nirva/AppData/Local/Programs/Python/Python37/:${PATH}

PROJECT=organism
OUTPUT_DIR=path/to/results/folder
INPUT_FILE=sample_run.in
ARCHITECT=path/to/Architect

module load conda2
python ${ARCHITECT}/architect/set_up_individual_tools.py --arguments_file $INPUT_FILE --project_name $PROJECT --output_dir $OUTPUT_DIR --architect_path $ARCHITECT
python ${ARCHITECT}/architect/run_individual_tools.py --project_name $PROJECT --output_dir $OUTPUT_DIR
python ${ARCHITECT}/architect/format_raw_results.py --project_name $PROJECT --output_dir $OUTPUT_DIR --arguments_file $INPUT_FILE --architect_path $ARCHITECT
python ${ARCHITECT}/architect/run_ensemble_approach.py --arguments_file $INPUT_FILE --project_name $PROJECT --output_dir $OUTPUT_DIR --architect_path $ARCHITECT 
python ${ARCHITECT}/architect/construct_metabolic_model.py --project_name $PROJECT --output_dir $OUTPUT_DIR --arguments_file $INPUT_FILE --project_name $PROJECT --architect_path

#IPR