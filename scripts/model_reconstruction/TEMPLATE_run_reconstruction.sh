module load NiaEnv/2018a # Needed for Niagara users.

# Need diamond; may be specific to Niagara users.
module load diamond

# Need Pandas; may be specific to Niagara users.
module load anaconda3

# Need CPLEX optimizer, and FRAMED, and CarveMe.
CPLEX_PATH=path/to/cplex
FRAMED_PATH=path/to/Architect/dependency
CARVEME_PATH=path/to/Architect/dependency
export PYTHONPATH=${PATH}:${CPLEX_PATH}:${FRAMED_PATH}:${CARVEME_PATH}

# Path to Architect info: to be defined.
MODEL_RECONSTRUCTION_PATH=path/to/Architect/scripts/model_reconstruction
DATABASE=path/to/Database/model_reconstruction
gapfill_script=path/to/Architect/dependency/CarveMe/scripts/gapfill_modified

# Path to (ensemble) enzyme annotation results: to be defined.
ENZ_ANNOTATION_results=path_of_file_with_enz_annot_results
ADDITIONAL_ENZ_results=path_of_file_with_Architect_missed_predictions

# Path to user defined reactions: to be defined.
USER_DEFINED_reactions=path_of_file_with_user_defined_reactions

# Path to output of model reconstruction: to be defined.
OUTPUT_FOLDER=path/to/output_folder
OUTPUT_GAP_FILL=name_of_output_file
FINAL_OUTPUT_FOLDER=path/to/final_output_folder

# User-specified parameters.
NUM_SOLNS=number_of_solns
NUM_OUTPUT_MODELS=number_of_output_models

# Folder where this should be run.
cd ${OUTPUT_FOLDER}

# This command is overwritten directly.
python3.7 ${MODEL_RECONSTRUCTION_PATH}/0_get_high_conf_set_of_reactions_from_ec.py --ec_preds_file ${ENZ_ANNOTATION_results} --additional_preds_file ${ADDITIONAL_ENZ_results} --user_defined_file ${USER_DEFINED_reactions} --database ${DATABASE} --output_folder ${OUTPUT_FOLDER}

python3.7 ${MODEL_RECONSTRUCTION_PATH}/1_create_universe_set_of_reactions.py --database ${DATABASE} --output_folder ${OUTPUT_FOLDER}

python3.7 ${MODEL_RECONSTRUCTION_PATH}/2_create_reaction_scores_file.py --ec_preds_file ${ENZ_ANNOTATION_results} --database ${DATABASE} --output_folder ${OUTPUT_FOLDER}

python3.7 ${MODEL_RECONSTRUCTION_PATH}/3_identify_gap_filling_candidates.py --output_folder ${OUTPUT_FOLDER} --user_defined_file ${USER_DEFINED_reactions}

# This command is overwritten.
$gapfill_script ${OUTPUT_FOLDER}/SIMULATION_high_confidence_reactions_plus_essentials.xml -m M9 -o ${OUTPUT_GAP_FILL} --scoredb ${OUTPUT_FOLDER}/SIMULATION_reaction_scores.out --universe-file ${OUTPUT_FOLDER}/SIMULATED_reduced_universe_with_fva.xml --pool-size ${NUM_SOLNS} --pool-gap POOL_GAP

# This command is unnecessary but is performed as a way of computing the necessity and sufficiency of gap-filling solutions.
python3.7 ${MODEL_RECONSTRUCTION_PATH}/x_verify_solns_necessary_and_sufficient.py --output_folder ${OUTPUT_FOLDER} --user_defined_file ${USER_DEFINED_reactions} --gap_filling_sol_file ${OUTPUT_GAP_FILL}

# This command outputs model from gap-filling solutions.
python3.7 ${MODEL_RECONSTRUCTION_PATH}/x_output_models_from_gapfill_soln.py --output_folder ${OUTPUT_FOLDER} --user_defined_file ${USER_DEFINED_reactions} --gap_filling_sol_file ${OUTPUT_GAP_FILL} --num_output_models ${NUM_OUTPUT_MODELS} --final_output_folder ${FINAL_OUTPUT_FOLDER} --database ${DATABASE}