PATH=/cygdrive/c/Users/nirva/AppData/Local/Programs/Python/Python37/:${PATH}

PROJECT=organism
OUTPUT_DIR=path/to/results/folder
INPUT_FILE=sample_run.in
ARCHITECT=path/to/Architect

python architect/set_up_individual_tools.py --arguments_file $INPUT_FILE --project_name $PROJECT --output_dir $OUTPUT_DIR --architect_path $ARCHITECT


#IPR