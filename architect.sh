PATH=/cygdrive/c/Users/nirva/AppData/Local/Programs/Python/Python37/:${PATH}

PROJECT=organism
PROJECT_DIR=path/to/results/folder
INPUT_FILE=sample_run.in
ARCHITECT=path/to/Architect

python architect/set_up_individual_tools.py --arguments_file $INPUT_FILE --project_name $PROJECT --project_dir $PROJECT_DIR --architect_path $ARCHITECT


#IPR