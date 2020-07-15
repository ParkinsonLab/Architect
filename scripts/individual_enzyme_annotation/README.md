The scripts in each of these folders are templates for running the different tools, and ought to be adapted for use.

Currently, the scripts are for running on such a cluster with 40-core system as SciNet's Niagara (https://docs.computecanada.ca/wiki/Niagara).
As a consequence, many of the tools have been optimized to fully use 40 cores, either following fasta files being split into 40k parts (k being a natural number) or using some core feature of the program.

Details of each of the tools can be found in their respective publications:

* CatFam (Yu et al, 2009)

* DETECT (Nursimulu et al, 2018)

* EFICAz (Kumar et al, 2012)

* EnzDP (Nguyen et al, 2015)

* PRIAM (Claudel-Renard et al, 2003)

_Acknowledgements_

SciNet is funded by: the Canada Foundation for Innovation under the auspices of Compute Canada; the Government of Ontario; Ontario Research Fund - Research Excellence; and the University of Toronto.

_Bibliography_

Chris Loken et al 2010 J. Phys.: Conf. Ser. 256 012026 doi: (10.1088/1742-6596/256/1/012026)

Yu, C., et al., Genome-wide enzyme annotation with precision control: catalytic families (CatFam) databases. Proteins, 2009. 74(2): p. 449-60.

Nursimulu, N., et al., Improved enzyme annotation with EC-specific cutoffs using DETECT v2. Bioinformatics, 2018. 34(19): p. 3393-3395.

Kumar, N. and J. Skolnick, EFICAz2.5: application of a high-precision enzyme function predictor to 396 proteomes. Bioinformatics, 2012. 28(20): p. 2687-8

Nguyen, N.N., et al., ENZDP: Improved enzyme annotation for metabolic network reconstruction based on domain composition profiles. Journal of Bioinformatics and Computational Biology, 2015. 13(5).

Claudel-Renard, C., et al., Enzyme-specific profiles for genome annotation: PRIAM. Nucleic Acids Res, 2003. 31(22): p. 6633-9.