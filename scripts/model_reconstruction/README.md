This folder contains a set of scripts for model reconstruction.
Uses python v3. 

* _0_get_high_conf_set_of_reactions_from_ec.py_:

	Writes reactions from high-confidence ECs predicted for an organism, appending all spontaneous/non-enzymatic reactions.
	Also write predictions with low-confidence (but non-zero values).  
	Separately writes reactions with massless compounds.

* _1_create_universe_set_of_reactions.py_:

	1. Find low-confidence reactions from KEGG. Those are some of the gap-filling candidates.
	2. Look at the high-confidence network:
		Find deadends, and add exchange reactions. Those are additional gap-filling candidates.
	3. Add remaining KEGG reactions as gap-filling candidates.

* _2_create_reaction_scores_file.py_:

	Outputs the score of different gap-filling candidates.

* _3_identify_gap_filling_candidates.py_:

	Identifies potential gap-fillers to be then used in CarveMe-based gap-filler.

* _x_verify_solns_necessary_and_sufficient.py_:

	(Optional) Can be used to verify if the gap-filling solutions are necessary and sufficient for biomass production.
	Solutions are expected to be so; however, when trying to get alternate solutions in one run, this is not necessarily the case.
	Under investigation.

* _x_output_models_from_gapfill_soln.py_:

	Following gap-filling, this program outputs an SBML and Excel file of the gap-filled model. 

* _utils.py_:

	Various functions that are used in different scripts.
	
* TEMPLATE_run_reconstruction.sh:

	Template script for running model reconstruction.