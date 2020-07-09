- 0_format_raw_results.py: Formats the raw results from specified methods.  
	Arguments:
	

		--output_folder (required): Folder where the formatted results will be written to.  
									
		--fasta_file    (required): File containing the sequences that we have the predictions from.  
									
		--catfam_raw    (optional): Raw file containing all output from CatFam  
		
		--detect_raw	(optional): Raw file containing all output from DETECT ie. the output found in the .out file 
									
		--eficaz_raw    (optional): Raw file containing all output from EFICAz ie. the output found in the .ecpred file 
									
		--enzdp_raw	    (optional): Raw file containing all output from EnzDP ie. the output found in the .res file 
									
		--priam_raw	    (optional): Raw file containing all output from PRIAM ie. the output found in the seqsECs.txt file 

									
	Example usage:  
	python 0_format_raw_results.py --output_folder OUTPUT_FOLDER 
	--Catfam_raw all_catfam_results.out --fasta_file file_with_sequences.fa
	
	Re-formatted Catfam results are written to OUTPUT_FOLDER given raw results
	found in all_catfam_results.out.  In the case of DETECT and EnzDP, the
	headers should be preferably removed by the user. 
	
- 0_get_readable_results.py: Formats the results obtained from above 
	into a form that can be read easily by the ensemble approaches we have. 
	Arguments: 
		--input_folder, -i (required): folder containing all the formatted results 
								       (basically output from 0_format_raw_results.py) 
		--output_file, -o  (required): file with the readable predictions for the  
									   next steps. 
	
- run_ensemble_approach.py: Runs ensemble approach of choosing given the  
  formatted results put in readable format. 
	Arguments: 
		--input_file, -i    (required): File where all predictions from the  
										different methods are. 
		--training_data, -t (required): Folder where the training data is. 
		--output_folder, -o (required): Folder where the predictions are going  
										to be written. 
		--method, -m        (optional): The ensemble method to run (default is 
										random forest). 
										Options are: 
										- Majority 
										- EC_specific 
										- NB 
										- Regression 
										- RF 
		--arguments, -a     (optional): Additional parameters to override 
										default ones (*) for ensemble methods. 
										- Majority: [1, 2*, 3], [high*, low] 
										- EC_specific: [all*, high] 
										- NB: [bernouilli*, binomial], [all*, high] 
										- Regression: [balanced, not_balanced*] 
										- RF: [ec_specific, generic*],  
											[balanced, not_balanced*, balanced_subsample] 
					
- x_list_ecs_left_out_by_RF_classifier.py: Lists the ECs predicted by each tool 
	for which there is no trained random forest classifier (default settings).   
	Separates those ECs	based on the level of confidence with which they are  
	predicted--as per the cutoffs I used for the random forest classifier. This  
	is an optional script.	 				
  
- different_ensemble_approaches.py: File containing the different ensemble 
  approaches that are run from 1_run_ensemble_approach.py. 
  
- utils.py: File containing functions that can be used for processing input from 
	the user, as well as other functions that involve simple processing that can 
	be used in different scripts. 