_Customization steps are detailed here_

These scripts assume the presence of a folder called Split_seqs containing your sequences split into 40k parts.

(1) First, go to TEMPLATE_project.py, and specify the path to Split_seqs, and where you wish your results to be written. 
TEMPLATE_project.py is the template for individualize_project.sh.

(2) Then, run individualize_project, which writes a project file for each of the sequences in Split_seqs.

(3) Last, run run_enzdp.sh, which operates on the parameters given in each project file. 
EnzDP generates many intermediate files.  These are written onto the dev nodes (Niagara), and subsequently deleted.