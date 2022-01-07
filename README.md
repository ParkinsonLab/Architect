Currently, things on this page are being reshuffled and this repository is being updated.  We appreciate your patience in the meantime.

# Architect

Architect is a pipeline for automatic metabolic model reconstruction.  Given the protein sequences of an organism, enzyme annotation is first performed through ensemble approaches, followed by gap-filling.  

Architect is designed to be an interactive tool for model reconstruction.  Architect can either be run using Docker on a simple computer, or on a computer cluster such as [Niagara](https://docs.scinet.utoronto.ca/index.php/Niagara_Quickstart).  In specific instances, users not using Docker will have to ensure certain dependencies are fulfilled and that certain specific modifications are made; these are detailed in this document.  

For more information, please contact nnursimulu@cs.toronto.edu.

## Table of contents
1. Overview  
2. Set-up instructions   
    a. For using Architect using Docker (on a single machine)  
    b. For using Architect without using docker and on Niagara or a Niagara-like system  
    c. Setting up Architect on an alternate system  
    d. Downloading CPLEX (required if performing model reconstruction)  
    e. Architect prerequisites  
3. Instructions for running Architect  
4. Output location  
5. Advanced parameter settings  
    a. Ensemble classifier for enzyme annotation  
    b. Inclusion of ECs not predicted by the ensemble classifier for model reconstruction  
    c. Inclusion of non-EC related reactions (when performing reconstructions using BiGG definitions)  
    d. Settings for gap-filling  
    e. Number of output models  
6. References  

# 1. Overview

This section details the steps going from protein sequence to gap-filled model.  For specific instructions regarding set-up and running Architect, please scroll down to the appropriate section.

1.	First, Architect runs your protein sequences through the different enzyme annotation tools (CatFam, DETECT, EFICAz, EnzDP, PRIAM).  One of the tools used—EnzDP—is slightly modified form its original version.  Modifications of EnzDP required for its use by Architect are listed in dependency/EnzDP.  
*	If you are using Architect on a computer cluster, these tools will run _in_ _parallel_ with each other, Architect itself will exit and you will need to independently monitor the progression of the corresponding jobs. Once these jobs have finished running, you will need to re-run Architect and specify that you do not need to run any individual enzyme annotation tools.
*	If using Architect with docker, these tools will run _sequentially_.  This step can be time-consuming.  Modifications for this step will be detailed in this document.

2.	The results are then formatted and run through an ensemble approach (default: naïve Bayes) using scripts in the folder scripts/ensemble_enzyme_annotation.

3.	Given the EC predictions with their corresponding likelihood scores and user-specified parameters (parameters as specified in such as file as ``sample_run.in``), a draft metabolic network is constructed then gap-filled.  This is performed using scripts found in scripts/model_reconstruction.  This uses a modified version of CarveMe, with scripts that can be found in dependency/CarveMe.  The framed package—modified from its original published form—is also required (in dependency/framed).
The final output comes in the form of a simple Excel file, as well as an SBML file annotated with links from KEGG/BiGG identifiers to other databases.

If not using Docker, users need to download certain ''database'' files specific to Architect; these are available in the folder Database on the Parkinson lab’s website at http://compsysbio.org/projects/Architect. (Details are given below.)

The manuscript for Architect is currently in preparation.  Please cite the tools that Architect uses when using our approach:

* CatFam (Yu et al, 2009)
* DETECT (Hung et al, 2010; Nursimulu et al, 2018)
* EFICAz (Kumar et al, 2012)
* EnzDP (Nguyen et al, 2015)
* PRIAM (Claudel-Renard et al, 2003)
* CarveMe (Machado et al, 2018)


# 2. Set-up instructions

When Architect was built, it was in many ways optimized for use by a supercomputer.  This, in particular, concerns the scripts used for running the individual tools.  Architect was tested using the Niagara supercomputer based at the University of Toronto.  For convenience, we provide alternative methods for running Architect with different set-up instructions as outlined below.

## a. For using Architect using Docker (on a single machine)

If you intend to run Architect on a laptop or computer, you may use our Docker image.  Please follow the following instructions.
1. First, install Docker on your machine ([Windows instructions](https://docs.docker.com/desktop/windows/install/) and [Mac instructions](https://docs.docker.com/desktop/mac/install/)).  Please make sure that your machine satisfies the system requirements listed.
2. Set up a folder [with the contents of the folder Dockerfile](https://github.com/ParkinsonLab/Architect/tree/master/Dockerfile), respecting the directory structure and the names of the files. 
3. If you do not intend to perform model reconstruction, ignore this step.  Otherwise, download the CPLEX optimizer as per the instructions given [below](#user-content-downloading-cplex-required-if-performing-model-reconstruction).  At the end, you will have a file called cplex_installer.bin.  Move this file to the folder containing the file called Dockerfile.
4. Go to command line, navigate to the folder containing the Dockerfile, and run the following command in command line.

	`docker build -t local_architect . `
5. Next, run the following command to download the enzyme annotation tools used by Architect to a pre-existing folder (called `<local-dir>` below).  Make sure that `local-dir` is the complete path to the folder of interest.  Note that this command will demand input from you.

	`docker run -v <local-dir>:/indiv_tools -it local_architect python2 Architect/downloader_of_tools.py`

Keep in mind that running enzyme annotation tools (as part of Architect's first step) on a single machine will likely take hours, if not, days, partly because the tools will be run consecutively rather than in parallel.  To deal with this, you may choose to limit the number of tools you wish to run, or run these tools separately (as outlined below).

## b. For using Architect on Niagara

Architect can be run as an end-to-end tool independently of Docker.  The following details steps to run Architect on [Niagara](https://docs.scinet.utoronto.ca/index.php/Niagara_Quickstart).

1. Get a copy of the code for Architect.  For example, you may use:

	```
	git clone https://github.com/parkinsonlab/architect
	```

2. Download the Database folder required for running Architect.  This file is present on the Parkinson lab's website [in a readable format](http://compsysbio.org/projects/Architect/Database/) and as [a tarred file](http://compsysbio.org/projects/Architect/Database.tar.gz).  On command line, you may use:

	```
	wget http://compsysbio.org/projects/Architect/Database.tar.gz
	tar -xzvf Database.tar.gz
	```

	Note: Following the first run of Architect, this folder and its contents will be modified; please be mindful of possible complications due to size requirements when you decide where to store this folder. (I have found this database to end up taking up a little over 1 GB of space following the first run of Architect.)

3. (If you do not intend to perform model reconstruction, ignore this step.)  Install the CPLEX optimizer as per the instructions given [below](#user-content-downloading-cplex-required-if-performing-model-reconstruction) and install CPLEX on your machine.

4. Next, the following tools should be installed.  Please follow the instructions below and choose the files specific to your system.  Please unpack the files for BLAST+, legacy BLAST and DIAMOND (for example using `tar -xzvf <file.tar.gz>`).

	| Tool                        | Location  |
	|-----------------------------|-----------|
	|BLAST+                       |Download from [here](http://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.7.1)|
	|BLAST (legacy version 2.2.26)|Download from [here](https://ftp.ncbi.nlm.nih.gov/blast/executables/legacy.NOTSUPPORTED/2.2.26/)|
	|DIAMOND                      |Download from [here](https://github.com/bbuchfink/diamond/releases/)|
	|EMBOSS                       |You may follow instructions such as [these](http://emboss.open-bio.org/html/adm/ch01s01.html).|

	In the case of EMBOSS, if you have a linux shell, you may run the following (for wish you need the `cmake` package):

	```
	wget ftp://emboss.open-bio.org/pub/EMBOSS/EMBOSS-6.6.0.tar.gz
	tar -xzvf EMBOSS-6.6.0.tar.gz
	cd EMBOSS-6.6.0
	sh configure
	make
	```

5. Now, a number of enzyme annotation tools need to be installed.  To install these tools, navigate to the directory where you downloaded the code for Architect, and run the following command (using python v2).  (Note that this requires user input.)

	```
	python2 downloader_of_tools.py --i yes
	``` 

Installation of all enzyme annotation tools is recommended. The section entitled [Architect prerequisites](#e-Architect-prerequisites) outlines some of the details of the tools used, in particular from where the enzyme annotation tools may be otherwise manually downloaded.


## c. Setting up Architect on an alternate system

### Step 1: Python v2 and v3 installations

For using Architect without Docker and outside of Niagara, we require that you have both v2 and v3 of Python installed (Architect has been tested on v2.7.16 and v3.7.1). In particular, it is easiest if you have the conda2 and anaconda3 packages installed.  (If you only need to perform enzyme annotation, conda2 suffices.)

Then, ensure the following two sets of dependencies are fulfilled.  (You can check this by entering ``import <package>`` in your python shell).  
*	In your python2 distribution, make sure you have the following packages: ``argparse``, ``numpy``, ``sklearn``, and ``biopython``.  
*	In your python3 distribution, make sure you have the following packages: ``argparse``, ``numpy``, ``biopython`` and ``libsbml``.
	
Otherwise, given the directory DIR where anaconda3/conda2 is installed, you may enter the following command in your shell window for installing biopython and libsbml for example:

```
$DIR/bin/conda install -y biopython
$DIR/bin/conda install -y -c SBMLTeam python-libsbml
``` 

### Step 2: Modification of specific scripts

When Architect was built, it was in many ways optimized for use by a supercomputer.  This, in particular, concerns the scripts used for running the individual enzyme annotation tools, although smaller modifications are required for model reconstruction.  Following download of Architect ([same 1st step for using Architect on Niagara](#b-For-using-Architect-on-Niagara)), please follow the following instructions.
*	If you are using a supercomputer (other than Niagara) which uses the SLURM job scheduler, please make any necessary modifications that are specific to your system to the following. (Please do not change the line numbers on which each remaining line of code appears as line number is important to Architect's functionality.)

	- Template scripts for each tool under scripts/individual_enzyme_annotation
	- TEMPLATE_run_reconstruction.sh under scripts/model_reconstruction
	- Verify that the lines starting with ``module load`` point towards a package you have in your system.  Otherwise, consider adding the directory with the package to your PATH variable.
	

* If you are using a supercomputer which does not use the SLURM job scheduler, please also follow the above instructions.  In addition, while ensuring not to change the line numbers on which each remaining line of code appears: 
	- Modify the header for your specific system.  
	- Modify the lines starting with ``module load`` as per your system. If the package in question is not available, you may consider adding the corresponding path to your PATH variable.

* If you are not using a supercomputer, please do the following:

	- Run the individual EC annotation tools then provide the results to Architect (You may use as an example the template scripts in scripts/individual_enzyme_annotation or even under scripts/individual_enz_annot_docker). More instructions are provided below for how this can be done.
	- Comment out line 1 of TEMPLATE_run_reconstruction.sh.
	- Comment out other lines starting with ``module load``.  Instead add the corresponding package to the PATH variable.  Make sure as you are doing so that you are not changing the line number where any remaining piece of code appears.
	
### Step 3: Complete set-up.

Follow steps 2 onwards as detailed [above](#b-For-using-Architect-on-Niagara).
	
TODO: MOVE THIS SECTION ELSEWHERE AS IT CAN BE USED FOR DOCKER. Results from individual enzyme annotation tools can be separately specified for use by Architect.  For this, please concatenate the main results from each tool into a single file.  (There is no need to do any special formatting to the raw results, such as removing headers.)  More instructions are provided below (TODO) for how this option can be used.

	
## d. Downloading CPLEX (required if performing model reconstruction)

Whether you are using Docker or not, you will need a CPLEX license to perform metabolic model reconstruction.  Free academic licenses can be obtained on the IBM website.  Here are some instructions for getting started:

1.	First make sure you have registered for an IBMId and password on the [IBM website](https://login.ibm.com/).
2.	Once you have logged in, go to https://www.ibm.com/academic/topic/data-science
3.	Scroll down and choose “Software” from the menu on the left.
4.	Choose “ILOG CPLEX Optimization Studio”.  Choose “Download” in the window that appears.
5.	If using Docker to run Architect, enter "CJ4Z5ML" in the field "Part numbers".  Select "IBM ILOG CPLEX Optimization Studio 12.9 for Linux x86-64 Multilingual (CNZM2ML)", scroll down and agree to the terms and conditions.  You will need the Download Director for downloading the installer.  Instructions will appear for installing the Download Director if you do not already have it installed.  Press "Details" in the window for the Download Director to find where the file is present.  
	*	Note: If not using Docker, download the installer for version 12.9 of CPLEX appropriate for your system (using "CJ4Z5ML" in the field "Part numbers") and run the installer.
6.	(Ignore this step if you are not using Docker)  Rename the bin file as cplex_installer.bin.  DO not run the installer by yourself.  This is done automatically when building the Docker image for your computer.

## e. Architect prerequisites

The following tools (version indicated in brackets) have been used to run Architect.  Installation of all enzyme annotation tools is recommended, and can be effectuated by running `downloader_of_tools.py`.

* BLAST+
* BLAST (v2.2.26)
* EMBOSS (v6.6.0)
* CatFam
* DETECT (v2)
* EFICAz (v2.5.1)
* EnzDP
* PRIAM (vJAN18)
* Cplex
* Diamond (v0.9.23.124)

The following table lists from where the enzyme annotation tools can be manually downloaded.


|Tool          | Location  |
|--------------|-----------|
|CatFam        | [Link](http://www.bhsai.org/downloads/catfam.tar.gz)|
|DETECT (v2)   | [Link](https://compsysbio.org/projects/DETECTv2/DETECTv2.tar.gz)|
|EFICAz (v2.5) | [Link](http://cssb2.biology.gatech.edu/4176ef47-d63a-4dd8-81df-98226e28579e/EFICAz2.5.1.tar.gz)|
|EnzDP         | [Link](https://bitbucket.org/ninhnn/enzdp/src/master/) |
|PRIAM (v2018) | [Database](http://priam.prabi.fr/REL_JAN18/Distribution.zip) and [search tool](http://priam.prabi.fr/utilities/PRIAM_search.jar) |

# 3. Instructions for running Architect

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

# 4. Output location

- The output from your run of Architect can be found at the location defined by $OUTPUT_DIR/$PROJECT in architect.sh.  
- Results from individual tools will be formatted within $OUTPUT_DIR/$PROJECT/Ensemble_annotation_files/Formatted_results. 
- Ensemble results will be found at $OUTPUT_DIR/$PROJECT/Ensemble_annotation_files/Ensemble_results.  
	- Results from the ensemble classifier will be in output_METHOD_OF_INTEREST.out in the format: 
	
	*EC\<tab\>sequence_name\<tab\>score\<tab\>any_additional_info*
	
	Results with a score of at least 0.5 in files of format output_METHOD_OF_INTEREST.out are considered of high-confidence.
	- Additional predictions of ECs that are not predictable by Architect will be output in output_preds_missed_out_METHOD_OF_INTEREST.out.  If you used a method that only considers high-confidence predictions from each tool, only left-out high-confidence predictions will be listed here. We recommend taking all supplementary high-confidence PRIAM predictions for enzyme annotation.
- Results from model reconstruction will be at $OUTPUT_DIR/$PROJECT/Model_reconstruction.  Final results will be in a subfolder called Final.  
	- If you run Architect multiple times, you will have multiple folders called Final_x (where x is a positive integer), the most recent results where x is highest.  
	- Intermediate results are written (and overwritten in the case of multiple runs) in a temp subfolder.  These files may be of interest for the modeller interested in looking at alternate solutions.
- The final output comes in the format of SBML or Excel files.  SBML files with the word "annotated" contain rich information such as mapping of identifiers from KEGG/BiGG to other databases.

# 5. Advanced parameter settings

At specific timepoints while running Architect, you will have the option to either choose a default setting or specify other settings more appropriate for your purposes.  In general, we highly recommend that the default setting be used.  However, depending on your specific situation, you may prefer to specify a setting other than the default.  Details about these alternate settings are given below.

## a.	Ensemble classifier for enzyme annotation

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

## b.	Inclusion of ECs not predicted by the ensemble classifier for model reconstruction

If you used any method other than any of the majority/voting rules for enzyme classification, there are EC predictions by individual tools that Architect will not necessarily be considering either due to the EC not figuring in the training data or due to the absence of a classifier for this EC. Given that this may impact model reconstruction, Architect will consider additional EC predictions by individual tools for this step. 

By default, Architect will take high-confidence EC predictions by PRIAM.  Otherwise, the user has the option to choose those predictions made with high-confidence by at least x tools, where x ranges from 1 to 5.

## c.	Inclusion of non-EC related reactions (when performing reconstructions using BiGG definitions)

When performing model reconstructions using reactions as defined by BiGG, non-EC related reactions will be added to the high-confidence model (that is, prior to gap-filling) based on sequence similarity. The E-value from these results is used to determine which of these reactions should be included in the model, the default being set at E-20.  The user may opt to use a different E-value as per their requirements.

## d.	Settings for gap-filling

When performing model reconstruction, the following is the set of (highly recommended) default settings:

1.	A single gap-filling solution is output.
2.	In the case where multiple solutions are output, a pool gap of 0.1 is utilized.
3.	An integrality tolerance of E-8 is used.
4.	A penalty of 1.0 is used for the addition of transport reactions for deadend metabolites.

Here, we provide some details about each of these parameter settings as well as any modifications that may be made as per the user's requirements (the setting number follows the one used above).

| Setting | Alternate option |
|---------|------------------|
| 1       | More than 1 gap-filling solution may be output by the user. At this time, we unfortunately cannot guarantee the optimality of these alternate solutions given the time complexity of the gap-filling step. <br/><br/>Note that if you choose to output more than one solution, you will later be asked how many output models you wish Architect to produce—more details [below](#5number-of-output-models).|
| 2       | This option is only applicable if the user wants to output multiple gap-filling solutions. The default option indicates that any solutions worse than 10% of the optimal will not be returned; please note that the value of a gap-filling solution is given by the sum of the penalties attributed to each of the gap-filling reactions in question.  <br/><br/>Setting this number lower will tighten the quality of solutions of interest, and the converse loosen these restrictions. |
| 3       | When performing gap-filling, an integer variable is assigned to each candidate gap-filling reaction, such that, in theory, a value of 1 is ascribed to the ith candidate gap-filling reaction if this reaction is part of the gap-filling solution being returned (and 0 otherwise). In practice however, the solver will not necessarily return integral variables. The integrality tolerance indicates how far from 0 or 1 a value can be to still be considered "integral".  <br/><br/>If you find that gap-filling is taking more time than desirable (for example, in my experience, gap-filling that takes longer than an hour and finishes on SciNet at the very least is rare), you may set this tolerance higher, for example, starting with E-7, then E-6 and so on.|
| 4       | By default, gap-filling candidate reactions associated with low-confidence EC predictions are associated with a penalty of addition less than 1. Remaining gap-filling candidate reactions that are part of the reaction database have a penalty of addition of 1.  As for transport reactions for deadend metabolites in the high-confidence network, they are associated with a default penalty of 1.  <br/><br/>If you wish to discourage the addition of such reactions, you can experiment with increasing this penalty. |

## e.	Number of output models

If you specify to Architect to output more than one gap-filling solution (say n solutions), you will have the option to output as many models ready for simulations (between 1 and n).  To be more specific, two sets of output can be obtained from Architect after running its model reconstruction module.

1.	Gap-filling solutions are, here, lists of reactions that can be used to obtain a model that is able to produce a minimum amount of the user-specified objective.  
	-	The output here is used in part to actually create the final SBML and Excel outputs. 
	-	These results can be found in $OUTPUT_DIR/$PROJECT/Model_reconstruction/temp.  
		-	The file SIMULATION_high_confidence_reactions.out contains high-confidence reactions (ie, prior to any gap-filling).
		-	The file ESSENTIAL_reactions.out contains the sets of reactions that are necessary for the user-defined objective to carry non-zero flux, and may include gap-filling reactions.  
		-	On the other hand, the file model_gapfilled_multi_x.lst will contain, on each line, alternate sets of reactions that can be used for gap-filling where x is the number of gap-filled solutions you wish to look at.
		-	You may consult the file model_gapfilled_multi_x.lst_check_nec_and_suff.out to get a sense of the quality of the solutions being output.  The column "Is_functional" indicates whether the model is functional with this current set of gap-filling reactions, and the column "All_reactions" essential" indicates if all these reactions are indispensable for non-zero flux through the objective function.  Ideally, both conditions will have been met; unfortunately, due to the complexity of the gap-filling problem, these may not be met, and currently we leave it up to the user to look through these alternate solutions.
	-	Please note that these results are overwritten whenever Architect's model reconstruction module is re-run in the same output folder.
2.	Gap-filled models are lists of reactions, complete with meta-data such as reaction name and metabolite name, that are ready to be used for constraints-based modeling. 
	- They are found in the Final_* folder under $OUTPUT_DIR/$PROJECT/Model_reconstruction and are available in Excel and SBML models.

The reason I separate these two kinds of outputs is that, in my experience, the SBML model output can be very large, and thus we leave it at the discretion of the user to determine the number of output models that is sensible to output.

# 6. References

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