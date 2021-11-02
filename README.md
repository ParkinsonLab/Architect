# Architect

Architect is a pipeline for automatic metabolic model reconstruction.  Given the protein sequences of an organism, enzyme annotation is first performed through ensemble approaches, followed by gap-filling.  Architect is designed to be an interactive tool for model reconstruction.

## Overview

This README details the steps going from protein sequence to gap-filled model.  Several parameters need to be defined in sample_run.in and a few more in sample_run.sh (more details below; note that either of these two files can be renamed).  Users only need to run the shell script sample_run.sh which goes through the following sequence of steps.

1.	First, Architect runs your protein sequences through the different enzyme annotation tools (CatFam, DETECT, EFICAz, EnzDP, PRIAM).  Alternately, these can be run by the user independently using details given in the folder scripts/individual_enzyme_annotation (also further details are given below).  One of the tools used—EnzDP—is slightly modified form its original version.  Modifications of EnzDP required for its use by Architect are listed in dependency/EnzDP.  
Please note that once these tools have started running using Architect, Architect will exit and you will need to independently monitor the progression of these tasks. 

2.	The results are then formatted and run through an ensemble approach (default: naïve Bayes) using scripts in the folder scripts/ensemble_enzyme_annotation.

3.	Given the EC predictions with their corresponding likelihood scores and user-specified parameters in sample_run.in, a draft metabolic network is constructed then gap-filled.  This is performed using scripts found in scripts/model_reconstruction.  This uses a modified version of CarveMe, with scripts that can be found in dependency/CarveMe.  The framed package—modified from its original published form—is also required (in dependency/framed).
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

# Specific instructions

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
* Diamond (v0.9.23.124)

In addition, to run Architect as an end-to-end tool, we require that you have both v2 and v3 of Python installed (Architect has been tested on v2.7.16 and v3.7.1). In particular, we require that you have the conda2 and anaconda3 packages installed.  (This requirement may be changed in a future iteration of Architect. If you only need to perform enzyme annotation, conda2 suffices.)  

Please make sure that you have downloaded the Architect-specific database available at http://compsysbio.org/projects/Architect/Database/.  Following the first run of Architect, this folder and its contents will be modified; please be mindful of possible complications due to size requirements when you decide where to store this folder. (I have found this database to end up taking up a little over 1 GB of space following the first run of Architect.)

### On which system do you intend to run Architect?

When Architect was built, it was in many ways optimized for use by a supercomputer.  This, in particular, concerns the scripts used for running the individual tools and model reconstruction.  Architect was tested using the Niagara supercomputer based at the University of Toronto.  If this is not your use case but you are using another supercomputer which uses the SLURM job scheduler, please make any necessary modifications that are specific to your system to the following:

- Template scripts for each tool under scripts/individual_enzyme_annotation
- TEMPLATE_run_reconstruction.sh under scripts/model_reconstruction
	
Please do not change the line numbers on which each remaining line of code appears as line number is important to Architect's functionality.

If you are not using a supercomputer, please consider doing the following:

- Running the individual EC annotation tools using the template scripts in scripts/individual_enzyme_annotation, then running Architect separately.
- Only commenting out line 1 of TEMPLATE_run_reconstruction.sh.
	
Results from individual enzyme annotation tools can be separately specified for use by Architect.  For this, please concatenate the main results from each tool into a single file, while ensuring that you remove any headers from the files.
	
## Running Architect

To run Architect, you first need to modify architect.sh and sample_run.in in this folder.

For architect.sh, specify the project name ($PROJECT), the output folder where you want Architect to output files ($OUTPUT_DIR), an input file specifying various parameters ($INPUT_FILE--takes the format of sample_run.in), and the path to the Architect folder ($ARCHITECT).

For sample_run.in, please specify the values as directed in the file.  In particular:

- PRIAM_db (*recommended*) is the file containing various enzyme profiles required for PRIAM's run.  
- SEQUENCE_FILE (*required*) denotes the fasta file of protein sequences you want to annotate with ECs.
- DATABASE (*required*) denotes the path to the Architect-specific database that can be downloaded [here]( http://compsysbio.org/projects/Architect/Database/)
- USER_def_reax (may be *required*) denotes user-defined reactions for model reconstruction.  To create this file, please consult sample_run_user_defined.txt for an example file.
- WARNING_mets (*optional*) is meant to override a set of reactions (concerning particular metabolites) that Architect automatically does not consider for model reconstruction; this only concerns models reconstructed using the KEGG database.  In particular, refer to the file [here](http://compsysbio.org/projects/Architect/Database/model_reconstruction/KEGG_universe/WARNING_reactions_with_formulaless_cpds.out)
	- If you want reactions concerning any of these metabolites to be considered for model reconstruction, please list them line by line in this file.  (This may, for example, concern metabolites that are acceptor/donor pairs but which are being excluded as no formula was found for them.) 
	- Otherwise, if you wish to use default settings or will use BiGG reactions for model reconstruction, please refer to a blank file here.
	
The first 10 keys concern enzyme annotation specific scripts, and the remainder model reconstruction.  If model reconstruction is not to be performed, please put a non-empty string value for these last keys.

## Output location

- The output from your run of Architect can be found at the location defined by $OUTPUT_DIR/$PROJECT in architect.sh.  
- Results from individual tools will be formatted within $OUTPUT_DIR/$PROJECT/Ensemble_annotation_files/Formatted_results. 
- Ensemble results will be found at $OUTPUT_DIR/$PROJECT/Ensemble_annotation_files/Ensemble_results.  
	- Results from the ensemble classifier will be in output_METHOD_OF_INTEREST.out in the format: 
	
	*EC\<tab\>sequence_name\<tab\>score\<tab\>any_additional_info*
	
	Results with a score of at least 0.5 in files of format output_METHOD_OF_INTEREST.out are considered of high-confidence.
	- Additional predictions of ECs that are not predictable by Architect will be output in output_preds_missed_out_METHOD_OF_INTEREST.out.  If you used a method that only considers high-confidence predictions from each tool, only left-out high-confidence predictions will be listed here. We recommend taking all supplementary high-confidence PRIAM predictions for enzyme annotation.
- Results from model reconstruction will be at $OUTPUT_DIR/$PROJECT/model_reconstruction.  Final results will be in a subfolder called Final.  
	- If you run Architect multiple times, you will have multiple folders called Final_x (where x is a positive integer), the most recent results where x is highest.  
	- Intermediate results are written (and overwritten in the case of multiple runs) in a temp subfolder.  These files may be of interest for the modeller interested in looking at alternate solutions.
- The final output comes in the format of SBML or Excel files.  SBML files with the word "annotated" contain rich information such as mapping of identifiers from KEGG/BiGG to other databases.

# Advanced parameter settings

At specific timepoints while running Architect, you will have the option to either choose a default setting or specify other settings more appropriate for your purposes.  In general, we highly recommend that the default setting be used.  However, depending on your specific situation, you may prefer to specify a setting other than the default.  Details about these alternate settings are given below.

## 1.	Ensemble classifier for enzyme annotation

The default ensemble classifier is the naïve Bayes classifier trained on high-confidence predictions by individual tools.  Other methods of ensemble classification may alternately be used as detailed below.  For each of these methods, additional parameters need to be specified; here, as well, the user has the option to use a default set of additional parameters.

| Method      | Brief description     | Default additional parameter | Other possible additional parameters |
| ----------- | ----------------------|----------------------------- | ------------------------------------ |
| Majority    | Majority rule         | 2/high                       | [1, 1.5, 2, 3, 3.5]/[high, low]      |
| EC_specific | EC-specific best tool | all                          | [all/high]                             |
| NB          | Naïve Bayes           | bernouilli/all               | [bernouilli]/[all, high]             |
| Regression  | Logistic regression   | not_balanced/l1              | [balanced, not_balanced], [l1, l2]   |
| RF          | Random forest         | ec_specific/not_balanced     | [ec_specific]/[balanced, not_balanced, balanced_subsample]|

Here, the value in the "Method" column should be specified to Architect, and if the additional parameters are not taken as the default, they can be specified by concatenating values from each of the lists (as given by the square brackets), delimiting each value by "/" (in a similar fashion to how the default additional parameters are specified above).

In the case of majority rule, the first parameter determines the kind of voting rule to be used (detailed below), and "high" and "low" indicate whether only high-confidence predictions or all predictions by individual tools are considered. 

| Voting rule | Explanation                                                                 |
|-------------|-----------------------------------------------------------------------------|
|1            |EC is assigned if predicted by at least 3 tools.                             |
|1.5          |EC is assigned if predicted by at least 1/2 of tools that can predict the EC.|
|2            |EC is assigned when predicted by most tools.                                 |
|3            |EC is assigned when predicted by all 5 tools.                                |
|3.5          |EC is assigned when predicted by all tools that can predict the EC.          |

In the case of the EC-specific best tool, a final EC is output if it is made by the top-performing tool(s) for that EC as found in training.  The difference between "high" and "all" settings lies in the section of the training data where these top-performers are identified.  More specifically, "high" refers to those tools found to be top-performers across all subsections of the training data, whereas "all" refers to those tools giving high performance in at least one subsection of the training data (but not necessarily on all subsections).

## 2.	Inclusion of ECs not predicted by the ensemble classifier for model reconstruction

If you used any method other than any of the majority/voting rules for enzyme classification, there are EC predictions by individual tools that Architect will not necessarily be considering either due to the EC not figuring in the training data or due to the absence of a classifier for this EC. Given that this may impact model reconstruction, Architect will consider additional EC predictions by individual tools for this step. 

By default, Architect will take high-confidence EC predictions by PRIAM.  Otherwise, the user has the option to choose those predictions made with high-confidence by at least x tools, where x ranges from 1 to 5.

## 3.	Inclusion of non-EC related reactions (when performing reconstructions using BiGG definitions)

When performing model reconstructions using reactions as defined by BiGG, non-EC related reactions will be added to the high-confidence model (that is, prior to gap-filling) based on sequence similarity. The E-value from these results is used to determine which of these reactions should be included in the model, the default being set at E-20.  The user may opt to use a different E-value as per their requirements.

## 4.	Settings for gap-filling

When performing model reconstruction, the following is the set of (highly recommended) default settings:

1.	A single gap-filling solution is output.
2.	In the case where multiple solutions are output, a pool gap of 0.1 is utilized.
3.	An integrality tolerance of E-8 is used.
4.	A penalty of 1.0 is used for the addition of transport reactions for deadend metabolites.

Here, we provide some details about each of these parameter settings as well as any modifications that may be made as per the user's requirements (the setting number follows the one used above).

| Setting | Alternate option |
|---------|------------------|
| 1       | More than 1 gap-filling solution may be output by the user. At this time, we unfortunately cannot guarantee the optimality of these alternate solutions given the time complexity of the gap-filling step. <br/><br/>Note that if you choose to output more than one solution, you will later be asked how many output models you wish Architect to produce—more details [below.](##5.	Number-of-output-models)|
| 2       | This option is only applicable if the user wants to output multiple gap-filling solutions. The default option indicates that any solutions worse than 10% of the optimal will not be returned; please note that the value of a gap-filling solution is given by the sum of the penalties attributed to each of the gap-filling reactions in question.  <br/><br/>Setting this number lower will tighten the quality of solutions of interest, and the converse loosen these restrictions. |
| 3       | When performing gap-filling, an integer variable is assigned to each candidate gap-filling reaction, such that, in theory, a value of 1 is ascribed to the ith candidate gap-filling reaction if this reaction is part of the gap-filling solution being returned (and 0 otherwise). In practice however, the solver will not necessarily return integral variables. The integrality tolerance indicates how far from 0 or 1 a value can be to still be considered "integral".  <br/><br/>If you find that gap-filling is taking more time than desirable (for example, in my experience, gap-filling that takes longer than an hour and finishes on SciNet at the very least is rare), you may set this tolerance higher, for example, starting with E-7, then E-6 and so on.|
| 4       | By default, gap-filling candidate reactions associated with low-confidence EC predictions are associated with a penalty of addition less than 1. Remaining gap-filling candidate reactions that are part of the reaction database have a penalty of addition of 1.  As for transport reactions for deadend metabolites in the high-confidence network, they are associated with a default penalty of 1.  <br/><br/>If you wish to discourage the addition of such reactions, you can experiment with increasing this penalty. |

## 5.	Number of output models

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