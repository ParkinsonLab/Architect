# Architect

Architect is a pipeline for automatic metabolic model reconstruction.  Given the protein sequences of an organism, enzyme annotation is first performed through ensemble approaches, followed by gap-filling.  Architect is designed to be an interactive tool for model reconstruction.

## Overview

This README details the steps going from protein sequence to gap-filled model.  Several parameters need to be defined in sample_run.in and a few more in sample_run.sh (more details below; note that either of these two files can be renamed).  Users only need to run the shell script sample_run.sh which goes through the following sequence of steps.

(1)	First, Architect runs your protein sequences through the different enzyme annotation tools (CatFam, DETECT, EFICAz, EnzDP, PRIAM).  Alternately, these can be run by the user independently using details given in the folder scripts/individual_enzyme_annotation (also further details are given below).  One of the tools used—EnzDP—is slightly modified form its original version.  Modifications of EnzDP required for its use by Architect are listed in dependency/EnzDP.  
Please note that once these tools have started running using Architect, Architect will exit and you will need to independently monitor the progression of these tasks. 

(2)	The results are then formatted and run through an ensemble approach (default: naïve Bayes) using scripts in the folder scripts/ensemble_enzyme_annotation.

(3)	Given the EC predictions with their corresponding likelihood scores and user-specified parameters in sample_run.in, a draft metabolic network is constructed then gap-filled.  This is performed using scripts found in scripts/model_reconstruction.  This uses a modified version of CarveMe, with scripts that can be found in dependency/CarveMe.  The framed package—modified from its original published form—is also required (in dependency/framed).
The final output comes in the form of a simple Excel file, as well as an SBML file annotated with links from KEGG/BiGG identifiers to other databases.

Users need to download certain files to run Architect; these are available in the folder Database on the Parkinson lab’s website at http://compsysbio.org/projects/Architect. 

The manuscript for Architect is currently in preparation.  Please cite the tools that Architect uses when using our approach:

	* CatFam (Yu et al, 2009)
	* DETECT (Hung et al, 2010; Nursimulu et al, 2018)
	* EFICAz (Kumar et al, 2012)
	* EnzDP (Nguyen et al, 2015)
	* PRIAM (Claudel-Renard et al, 2003)
	* CarveMe (Machado et al, 2018)

For more information, please contact nnursimulu@cs.toronto.edu

# Other specific instructions

## Set-up

In order to run Architect, please make sure that you have the following tools installed (in brackets the version is indicated).  Installation of all enzyme annotation tools is recommended.

	* BLAST (v2.2.26)
	* EMBOSS (v6.6.0)
	* CatFam
	* DETECT (v2)
	* EFICAz (v2.5.1)
	* EnzDP
	* PRIAM (vJAN18)
	* Cplex
	* diamond (v0.9.23.124)

In addition, to run Architect as an end-to-end tool, we require that you have both v2 and v3 of Python installed (Architect has been tested on v2.7.16 and v3.7.1). In particular, we require that you have the conda2 and anaconda3 packages installed.  (This requirement may be changed in a future iteration of Architect. If you only need to run enzyme annotation, conda2 suffices.)  

Please make sure that you have downloaded the Architect-specific database available at http://compsysbio.org/projects/Architect/Database/.  Following the first run of Architect, this folder and its contents will be modified; please be mindful of possible complications due to size requirements when you decide where to store this folder. (I have found this database to end up taking up a little over 1 GB of space following the first run of Architect.)

In addition, when Architect was built, it was in many ways optimized for use by a supercomputer.  This, in particular, concerns the scripts used for running the individual tools and model reconstruction.  Architect was tested using the Niagara supercomputer based at the University of Toronto.  If this is not your use case but you are using another supercomputer which uses the SLURM job scheduler, please make any necessary modifications to the following that are specific to your system:

	- template scripts under each folder under scripts/individual_enzyme_annotation
	- TEMPLATE_run_reconstruction.sh under scripts/model_reconstruction
	
Please ensure to not change the line numbers on which each remaining line of code appears as line number is sensitive to Architect's code.

If you are not using a supercomputer, please consider doing the following:

	- running the individual EC annotation tools using the template scripts in scripts/individual_enzyme_annotation, then running Architect separately.
	- Only commenting out line 1 of TEMPLATE_run_reconstruction.sh.
	
Results from individual enzyme annotation tools can be separately specified for use by Architect.  For this, please concatenate the main results from each tool into a single file, while ensuring that you remove any headers from the files.
	
## Running Architect

To run Architect, you first need to modify architect.sh and sample_run.in in this folder.

For architect.sh, specify the project name (PROJECT), the output folder where you want Architect to output files (OUTPUT_DIR), an input file specifying various parameters (INPUT_FILE--takes the format of sample_run.in), and the path to the Architect folder (ARCHITECT).

For sample_run.in, please specify the values as directed in the file.  In particular:

	- PRIAM_db is the file containing various enzyme profiles required for PRIAM's run.  
	- SEQUENCE_FILE denotes the fasta file of protein sequences you want to annotate with ECs.  \
	- DATABASE denotes the path to the Architect-specific database that can be downloaded at http://compsysbio.org/projects/Architect/Database/
	- USER_def_reax denotes user-defined reactions for model reconstruction.  To create this file, please consult sample_run_user_defined.txt for an example file.
	- WARNING_mets contains a list of metabolites whose reactions are thought can be be considered for model reconstruction; this concerns models reconstructed using the KEGG database.  Note that not all reactions downloaded from KEGG will be considered for reconstruction.  In particular, refer to the file at http://compsysbio.org/projects/Architect/Database/model_reconstruction/KEGG_universe/WARNING_reactions_with_formulaless_cpds.out
	If you want reactions concerning any of these metabolites, please list them line by line in this file.  (This may concern metabolites that are acceptor/donor pairs for instance.)
	Otherwise, please refer to a blank file here.
	
The first 10 keys concern enzyme annotation specific scripts, and the remainder model reconstruction.  If model reconstruction is not to be performed, please put a non-empty string value for these last keys.

## Output and location

The output from your run of Architect can be found at the location defined by $OUTPUT_DIR/$PROJECT in architect.sh.  
Results from individual tools will be formatted within $OUTPUT_DIR/$PROJECT/Ensemble_annotation_files/Formatted_results.  
Ensemble results will be found at $OUTPUT_DIR/$PROJECT/Ensemble_annotation_files/Ensemble_results.  

	- Results from the ensemble classifier will be in output_METHOD_OF_INTEREST.out in the format: EC<tab>sequence_name<tab>score<tab>any_additional_info. Results with a score of at least 0.5 in files of format output_METHOD_OF_INTEREST.out are considered of high-confidence.
	- Additional predictions of ECs that are not predictable by Architect will be output in output_preds_missed_out_METHOD_OF_INTEREST.out.  If you used a method that only considers high-confidence predictions from each tool, only left-out high-confidence predictions will be listed here. We recommend taking all supplementary high-confidence PRIAM predictions for enzyme annotation.
	
Results from model reconstruction will be at $OUTPUT_DIR/$PROJECT/model_reconstruction.  Final results will be in a subfolder called Final.  If you run Architect multiple times, you will have multiple folders called Final_x (where x is a positive integer), the most recent results where x is highest.  Intermediate results are written (and overwritten in the case of multiple runs) in a temp subfolder.  These files may be of interest for the modeller interested in looking at alternate solutions.

The final output comes in the format of SBML or Excel files.  SBML files with the word "annotated" contain rich information such as mapping of identifiers from KEGG/BiGG to other databases.

# References

Yu, C., et al., Genome-wide enzyme annotation with precision control: catalytic families (CatFam) databases. Proteins, 2009. 74(2): p. 449-60.

Hung, S.S., et al., DETECT--a density estimation tool for enzyme classification and its application to Plasmodium falciparum. Bioinformatics, 2010. 26(14): p. 1690-8.

Nursimulu, N., et al., Improved enzyme annotation with EC-specific cutoffs using DETECT v2. Bioinformatics, 2018. 34(19): p. 3393-3395.

Kumar, N. and J. Skolnick, EFICAz2.5: application of a high-precision enzyme function predictor to 396 proteomes. Bioinformatics, 2012. 28(20): p. 2687-8

Nguyen, N.N., et al., ENZDP: Improved enzyme annotation for metabolic network reconstruction based on domain composition profiles. Journal of Bioinformatics and Computational Biology, 2015. 13(5).

Claudel-Renard, C., et al., Enzyme-specific profiles for genome annotation: PRIAM. Nucleic Acids Res, 2003. 31(22): p. 6633-9.

Machado, D., et al., Fast automated reconstruction of genome-scale metabolic models for microbial species and communities. Nucleic Acids Res, 2018. 46(15): p. 7542-7553.

Buchfink, B. et al., Fast and sensitive protein alignment using DIAMOND.  Nature Methods, 2015. 12(1): p. 59-60.

CPLEX: available at https://www.ibm.com/analytics/cplex-optimizer

Ponce, M. et al., Deploying a Top-100 Supercomputer for Large Parallel Workloads: the Niagara Supercomputer. PEARC'19 Proceedings, 2019.