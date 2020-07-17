# Architect

Architect is a pipeline for automatic metabolic model reconstruction.  Given the protein sequences of an organism, enzyme annotation is first performed through ensemble approaches, followed by gap-filling.  This repository is currently in construction.

This README details the steps going from protein sequence to gap-filled model, as present in sample_run.sh.

(1)	First run your protein sequences through the different enzyme annotation tools (CatFam, DETECT, EFICAz, EnzDP, PRIAM).  Details are given in the folder scripts/individual_enzyme_annotation.  One of the tools used—EnzDP—is slightly modified form its original version.  The new set of scripts to be used for running EnzDP are found in dependency/EnzDP.

(2)	The results are then formatted then run through an ensemble approach (default: the random forest classifier) as given in the folder scripts/ensemble_enzyme_annotation.

(3)	Given the EC predictions and corresponding confidence scores, a draft metabolic network is constructed then gap-filled.  This is performed using scripts found in scripts/model_reconstruction.  This uses a modified version of CarveMe, scripts can be found in dependency/CarveMe.

Database files will be made available on the Parkinson lab’s website at http://compsysbio.org. 

The manuscript for Architect is currently in preparation.  Please cite the tools that Architect uses when using our approach:

	* CatFam (Yu et al, 2009)
	* DETECT (Hung et al, 2010; Nursimulu et al, 2018)
	* EFICAz (Kumar et al, 2012)
	* EnzDP (Nguyen et al, 2015)
	* PRIAM (Claudel-Renard et al, 2003)
	* CarveMe (Machado et al, 2018)

For more information, please contact nnursimulu@cs.toronto.edu

# Bibliography

Yu, C., et al., Genome-wide enzyme annotation with precision control: catalytic families (CatFam) databases. Proteins, 2009. 74(2): p. 449-60.

Hung, S.S., et al., DETECT--a density estimation tool for enzyme classification and its application to Plasmodium falciparum. Bioinformatics, 2010. 26(14): p. 1690-8.

Nursimulu, N., et al., Improved enzyme annotation with EC-specific cutoffs using DETECT v2. Bioinformatics, 2018. 34(19): p. 3393-3395.

Kumar, N. and J. Skolnick, EFICAz2.5: application of a high-precision enzyme function predictor to 396 proteomes. Bioinformatics, 2012. 28(20): p. 2687-8

Nguyen, N.N., et al., ENZDP: Improved enzyme annotation for metabolic network reconstruction based on domain composition profiles. Journal of Bioinformatics and Computational Biology, 2015. 13(5).

Claudel-Renard, C., et al., Enzyme-specific profiles for genome annotation: PRIAM. Nucleic Acids Res, 2003. 31(22): p. 6633-9.

Machado, D., et al., Fast automated reconstruction of genome-scale metabolic models for microbial species and communities. Nucleic Acids Res, 2018. 46(15): p. 7542-7553.
