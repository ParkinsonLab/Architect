_Customization steps are detailed here_

These scripts assume the presence of a folder called Split_seqs containing your sequences split into 40k parts.

(1) First, go to TEMPLATE_eficaz.sh, and customize as required.

(2) Then, run individualize_project, which creates eficaz_1.sh, eficaz_2.sh, ... eficaz_k.sh in folder Scripts.

(3) Run eficaz_1.sh, eficaz_2.sh, ... eficaz_k.sh.
EFICAz generates many intermediate files.  These are written onto the RAM disk (Niagara), and subsequently deleted.