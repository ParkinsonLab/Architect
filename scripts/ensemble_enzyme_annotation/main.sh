# 0. Set up locations of various things.
organism_folder=ORGANISM
raw_folder=${organism_folder}/RAW_results
fasta_file=${organism_folder}/file.fa
formatted_folder=${organism_folder}/FORMATTED_Results
readable_folder=${organism_folder}/READABLE_Results
readable_file=${readable_folder}/predicted_ec_to_proteins.out
results_folder=${organism_folder}/ENSEMBLE_Results
TRAINING_data=../Trained_data_python_v2

CATFAM_results=${raw_folder}/CatFam/Results
DETECT_results=${raw_folder}/DETECT/output_40.out
EFICAz_results=${raw_folder}/EFICAz/Results
EnzDP_results=${raw_folder}/EnzDP/Results
PRIAM_results=${raw_folder}/PRIAM/PRIAM_Results/PRIAM_test/ANNOTATION/sequenceECs.txt

catfam_results_2=${raw_folder}/CatFam/CONCATENATED_CatFam.out
detect_results_2=${raw_folder}/DETECT/CONCATENATED_DETECT.out
eficaz_results_2=${raw_folder}/EFICAz/CONCATENATED_EFICAz.out
enzdp_results_2=${raw_folder}/EnzDP/CONCATENATED_EnzDP.out
priam_results_2=${raw_folder}/PRIAM/CONCATENATED_PRIAM.out

# 1. Unzip EFICAz results.
for file in `ls $EFICAz_results/*`; do
	tar -xzvf $file -C $EFICAz_results;
done

# 2. Concatenate raw results.
python 0_concatenate_raw_results.py --output_folder $OUTPUT_FOLDER --catfam_results $CATFAM_results --detect_results $DETECT_results --eficaz_results $EFICAz_results --enzdp_results $EnzDP_results --priam_results $PRIAM_results

# 3. Format raw results.
mkdir -p ${formatted_folder}
python 0_format_raw_results.py --output_folder ${formatted_folder} --catfam_raw ${catfam_results_2} --detect_raw ${detect_results_2} --eficaz_raw ${eficaz_results_2} --enzdp_raw ${enzdp_results_2} --priam_raw ${priam_results_2} --fasta_file ${fasta_file};

# 4. Convert into a format that can be read easily.
mkdir -p ${readable_folder}
python 0_get_readable_results.py --input_folder ${formatted_folder} --output_file  ${readable_file} 

# 5. Run the default unbalanced random forest classifier.  Also write out the ECs that cannot be read by the trained classifier.
mkdir -p ${results_folder}
python 1_run_ensemble_approach.py --input_file ${readable_file} --training_data ${TRAINING_data} --output_folder ${results_folder};
python x_list_ecs_left_out_by_trained_classifier.py --input_file ${readable_file} --training_data ${TRAINING_data} --output_folder ${results_folder};