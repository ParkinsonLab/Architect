import os
import sys
from argparse import ArgumentParser
import datetime
import subprocess
import utils

def organize_enz_annot_results(main_folder_with_enzannot_results):

    enzannot_files = os.listdir(main_folder_with_enzannot_results)
    id_to_main_to_additional_results = {}
    i = 0
    for cur_file in enzannot_files:
        if "missed_out" in cur_file:
            continue
        additional_preds_file = "output_preds_missed_out_" + cur_file.split("output_")[1]
        id_to_main_to_additional_results[i] = [main_folder_with_enzannot_results + "/" + cur_file, main_folder_with_enzannot_results + "/" + additional_preds_file]
        i += 1
    return id_to_main_to_additional_results


if __name__ == '__main__':

    current_working_directory = os.getcwd()
    sys.path.append(current_working_directory)

    try:
        input = raw_input
    except NameError:
        pass

    parser = ArgumentParser(description="Constructs the metabolic model from the results of enzyme annotation.")
    parser.add_argument("--arguments_file", type=str, help="File with the values of the parameters.", required=True)
    parser.add_argument("--project_name", type=str, help="Name of the project (eg: organism name).", required=True)
    parser.add_argument("--output_dir", type=str, help="Location of project directory (default: current working directory).", required=False, default=current_working_directory)
    parser.add_argument("--architect_path", type=str, help="Location of Architect project directory", required=True)

    args = parser.parse_args()
    output_dir = args.output_dir
    project_name = args.project_name
    arguments_file = args.arguments_file
    architect_path = args.architect_path

    parameter_values = utils.read_parameter_values(arguments_file)

    # Get user-defined reactions, and the folder with the database.
    user_def_rxns = parameter_values["USER_def_reax"]
    main_database_folder = utils.get_shell_to_python_readable_location(parameter_values["DATABASE"])

    status_file = output_dir + "/" + args.project_name + "/architect_status.out"
    status_writer = open(status_file, "a")

    # First verify that the user has not quit.
    if utils.user_has_quit(status_file) or utils.just_ran_tools(status_file):
        exit()

    # Ask the user if they want to run model reconstruction; otherwise quit.
    answer = ""
    while answer not in ["Y", "N"]:
        answer = utils.input_with_colours("Architect: Do you wish to perform model reconstruction? Otherwise Architect will exit. [y/n] ")
        answer = answer.strip().upper()
        if answer == "N":
            status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
            status_writer.close()
            exit()

    # Have the model reconstruction dbs already been set up?  If not, ask the user if they want to proceed.
    model_reconstruction_folder = utils.get_shell_to_python_readable_location(parameter_values["DATABASE"]) + "/model_reconstruction"
    model_reconstruction_status_file = model_reconstruction_folder + "/classifier_set_up.out"
    if not utils.check_info_set_up(model_reconstruction_status_file, "Successfully set up all databases."):
        answer = ""
        while answer != "Y":
            answer = utils.input_with_colours("Architect: We have detected that the reaction databases have yet to be set up.  \
                \nArchitect: This is an essential step for running Architect's model reconstruction function.\n\
                Enter [y] to proceed. Otherwise, quit by entering [n]: ")
            answer = answer.strip().upper()

            if answer in ["Q", "N"]:
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                status_writer.close()
                utils.print_with_colours("Architect will now exit.")
                exit()

        status_writer.write("Set up:" + str(datetime.datetime.now()) + ": Model reconstruction dbs about to be set up.\n")
        utils.print_with_colours("Architect: Databases will now be set up.  This will take some time.")

        set_up_metanetx = ["python", architect_path + "/scripts/model_reconstruction/x_set_up_metanetx_dblinks.py"]
        set_up_metanetx.append("-d")
        set_up_metanetx.append(model_reconstruction_folder + "/MetaNetX")
        set_up_metanetx.append("-k")
        set_up_metanetx.append(model_reconstruction_folder + "/KEGG_universe")
        set_up_metanetx.append("-b")
        set_up_metanetx.append(model_reconstruction_folder + "/Common_BiGG_info")
        set_up_metanetx.append("-s")
        set_up_metanetx.append(model_reconstruction_status_file)
        subprocess.call(set_up_metanetx)

        set_up_kegg = ["python", architect_path + "/scripts/model_reconstruction/x_set_up_kegg_db.py"]
        set_up_kegg.append("-k")
        set_up_kegg.append(model_reconstruction_folder + "/KEGG_universe")
        set_up_kegg.append("-m")
        set_up_kegg.append(model_reconstruction_folder + "/MetaNetX")
        set_up_kegg.append("-s")
        set_up_kegg.append(model_reconstruction_status_file)
        subprocess.call(set_up_kegg)

        status_writer.write("Set up:" + str(datetime.datetime.now()) + ": Database set up is complete.\n")
        utils.print_with_colours("Architect: Database set up complete.")


    # Create model reconstruction output folder for temporary files used while performing model reconstruction
    main_folder_with_results = output_dir +  "/" + project_name
    main_folder_with_recon_results = main_folder_with_results + "/Model_reconstruction"
    temp_folder = main_folder_with_recon_results + "/temp"
    checks_folder = temp_folder + "/checks"
    additional_folder = temp_folder + "/additional"
    final_output_folder = main_folder_with_recon_results + "/Final"
    if not os.path.isdir(main_folder_with_recon_results):
        os.mkdir(main_folder_with_recon_results)
    if not os.path.isdir(temp_folder):
        os.mkdir(temp_folder)
    if not os.path.isdir(checks_folder):
        os.mkdir(checks_folder)
    if not os.path.isdir(additional_folder):
        os.mkdir(additional_folder)
    if not os.path.isdir(final_output_folder):
        os.mkdir(final_output_folder)
    else:
        i = 2
        final_output_folder_temp = final_output_folder
        while os.path.isdir(final_output_folder_temp):
            final_output_folder_temp = final_output_folder + "_" + str(i)
            i += 1
        os.mkdir(final_output_folder_temp)
        final_output_folder = final_output_folder_temp

    # Get the files in the enzyme annotation folder.  If there are multiple, ask the user which one to use.
    main_folder_with_enzannot_results = main_folder_with_results + "/Ensemble_annotation_files/Ensemble_results"
    id_to_main_results_to_left_out_preds = organize_enz_annot_results(main_folder_with_enzannot_results)
    if len(id_to_main_results_to_left_out_preds) == 1:
        enzannot_results_file = id_to_main_results_to_left_out_preds[0][0]
        additional_preds_file = id_to_main_results_to_left_out_preds[0][1]
    elif len(id_to_main_results_to_left_out_preds) > 1:
        utils.print_with_colours("Architect: there are multiple results from enzyme annotation.  Which would you like to use?  Choose the ID from the following: ")
        utils.print_with_colours("ID\tEnz_annot_results")
        file_identifiers = []
        for i in sorted(id_to_main_results_to_left_out_preds.keys()):
            info = id_to_main_results_to_left_out_preds[i]
            utils.print_with_colours(str(i) + "\t" + info[0])
            file_identifiers.append(str(i))
        file_id = -1
        while (file_id not in file_identifiers):
            file_id = utils.input_with_colours("Enter the ID you wish [0-" + str(len(file_identifiers) - 1) + "]: ")
            file_id = file_id.strip()
            if file_id == "Q":
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                status_writer.close()
                exit()
        enzannot_results_file = id_to_main_results_to_left_out_preds[int(file_id)][0]
        additional_preds_file = id_to_main_results_to_left_out_preds[int(file_id)][1]
    else:
        status_writer.write("Termination:" + str(datetime.datetime.now()) + ": ERROR: Missing files\n")
        utils.print_warning ("Architect: missing enzyme annotation files. Architect will now exit.")
        exit()

    # Get user feedback on how many predictions they wish to use.
    min_num_high_conf = ""
    answer = ""
    while answer not in ["Y", "N"]:
        answer = utils.input_with_colours("Architect: For ECs not predictable by Architect, include (default) high-confidence prediction by PRIAM? (HIGHLY RECOMMENDED) [y/n] ")
        answer = answer.strip().upper()
        if answer == "Q":
            status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
            status_writer.close()
            exit()
    if answer == "N":
        while min_num_high_conf not in ["1", "2", "3", "4", "5"]:
            min_num_high_conf = utils.input_with_colours("Architect: you wish to include high-confidence predictions by at least how many tools? [1-5]: ")
        status_writer.write("Step 5: " + str(datetime.datetime.now()) + \
            ": User wishes to include high-confidence predictions by at least " + min_num_high_conf + " tools.\n")
        min_num_high_conf = int(min_num_high_conf)
    else:
        status_writer.write("Step 5: " + str(datetime.datetime.now()) + \
            ": User wishes to use default, including high-confidence predictions by PRIAM.\n")

    # Get user feedback to tweak with parameters of gap-filling.
    answer = ""
    utils.print_with_colours("Architect will use the following parameters for model reconstruction (default):")
    utils.print_with_colours("- output a single gap-filling solution")
    utils.print_with_colours("- use a pool gap of 0.1")
    utils.print_with_colours("- use an integrality constraint of 10E-8")
    utils.print_with_colours("- use a penalty of 1.0 for the addition of transport reactions for deadend metabolites")

    while answer not in ["Y", "N"]:
        answer = utils.input_with_colours("Use default? (HIGHLY RECOMMENDED) [y/n] ")
        answer = answer.strip().upper()
        if answer == "Q":
            status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
            status_writer.close()
            exit()

    num_solns = 0
    pool_gap = 0.1
    integrality_constraint = ""
    penalty_deadend = ""
    if answer == "N":
        answer_1 = ""
        while answer_1 not in ["Y", "N"]:
            answer_1 = utils.input_with_colours("Architect: change number of gap-filling solutions from 1? [y/n] ")
            answer_1 = answer_1.strip().upper()
            if answer_1 == "Q":
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                status_writer.close()
                exit()
        if answer_1 == "Y":
            num_solns = ""
            while (not utils.is_int(num_solns)) or (int(num_solns) < 2):
                num_solns = utils.input_with_colours("Enter a number greater than 1 for the number of gap-filling solutions: ")
            num_solns = int(num_solns)
            status_writer.write("Step 5: " + str(datetime.datetime.now()) + \
                ": User wishes to change the number of solutions to " + str(num_solns) + ".\n")

        answer_2 = ""
        while answer_2 not in ["Y", "N"]:
            answer_2 = utils.input_with_colours("Architect: change size of gap pool from 0.1? [y/n] ")
            answer_2 = answer_2.strip().upper()
            if answer_2 == "Q":
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                status_writer.close()
                exit()
        if answer_2 == "Y":
            pool_gap = ""
            while (not utils.is_float(pool_gap)) or (float(pool_gap) > 1) or (float(pool_gap) <= 0):
                pool_gap = utils.input_with_colours("Enter a number between 0 and 1 for the gap pool: ")
            pool_gap = float(pool_gap)
            status_writer.write("Step 5: " + str(datetime.datetime.now()) + \
                ": User wishes to change the gap pool to " + str(pool_gap) + ".\n")

        answer_3 = ""
        while answer_3 not in ["Y", "N"]:
            answer_3 = utils.input_with_colours("Architect: change size integrality constraint from 10E-8? [y/n] ")
            answer_3 = answer_3.strip().upper()
            if answer_3 == "Q":
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                status_writer.close()
                exit()
        if answer_3 == "Y":
            integrality_constraint = ""
            while (not utils.is_float(integrality_constraint)) or (float(integrality_constraint) >= 1) or (float(integrality_constraint) <= 0):
                integrality_constraint = utils.input_with_colours("Enter a number between 0 and 1 for the integrality constraint: ")
            integrality_constraint = float(integrality_constraint)
            status_writer.write("Step 5: " + str(datetime.datetime.now()) + \
                ": User wishes to change the integrality constraint to " + str(integrality_constraint) + ".\n")

        answer_4 = ""
        while answer_4 not in ["Y", "N"]:
            answer_4 = utils.input_with_colours("Architect: change penalty for transporting deadend metabolites from 1.0? [y/n] ")
            answer_4 = answer_4.strip().upper()
            if answer_4 == "Q":
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                status_writer.close()
                exit()
        if answer_4 == "Y":
            penalty_deadend = ""
            while (not utils.is_float(penalty_deadend)):
                penalty_deadend = utils.input_with_colours("Enter a number for the penalty (greater than 1 penalizes more): ")
            penalty_deadend = float(penalty_deadend)
            status_writer.write("Step 5: " + str(datetime.datetime.now()) + \
                ": User wishes to change the penalty to " + str(penalty_deadend) + ".\n")

    # Which database does the user wish to use for model reconstruction?
    universe_id = ""
    id_to_universe = {"1": "KEGG_universe", \
        "2": "BiGG_main_universe", \
            "3": "BiGG_grampos_universe", \
                "4": "BiGG_gramneg_universe", \
                    "5": "BiGG_archae_universe", \
                        "6": "BiGG_cyano_universe"}
    utils.print_with_colours("Architect: which set of reactions would you like to use to build the model?  Choose the ID from the following:")
    utils.print_with_colours("ID\tSet_of_reactions")
    while universe_id not in ["1", "2", "3", "4", "5", "6"]:
        for idd in sorted(id_to_universe.keys()):
            universe = id_to_universe[idd]
            utils.print_with_colours(idd + "\t" + universe)
        universe_id = utils.input_with_colours("Enter the ID you wish [1-6]: ")
        universe_id = universe_id.strip()
        if universe_id.upper() == "Q":
            status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
            status_writer.close()
            exit()
    status_writer.write("Step 5: " + str(datetime.datetime.now()) + ": User wishes to use " + id_to_universe[universe_id] + " for model reconstruction.\n")
    universe_set_of_reactions = main_database_folder + "/model_reconstruction/" + id_to_universe[universe_id]

    # If the user has specified to use one of the BiGG database, ask what E-value they would like to use to include additional reactions.
    evalue_blastp = None
    if universe_id != "1":
        utils.print_with_colours("Architect: which e-value for BlastP would you like to use to include non-EC related reactions?")
        answer_evalue = ""
        while answer_evalue not in ["Y", "N", "Q"]:
            answer_evalue = utils.input_with_colours("Use default of E-20? (HIGHLY RECOMMENDED) [y/n]: ")
            answer_evalue = answer_evalue.strip().upper()
        if answer_evalue == "Q":
            status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
            status_writer.close()
            exit()
        if answer_evalue == "Y":
            evalue_blastp = 10**(-20)
        else:
            while (not utils.is_float(evalue_blastp)) or (float(evalue_blastp) < 0):
                evalue_blastp = utils.input_with_colours("Enter a positive number for the E-value: ")
            evalue_blastp = float(evalue_blastp)
        status_writer.write("Step 5: " + str(datetime.datetime.now()) + ": User wishes to use the E-value of " + str(evalue_blastp) + " for blastp.\n")


    # If the user asked for more than one gap-filling solution, ask the user how many gap-filled models they want.
    num_output_models = 1
    if num_solns >= 2:
        utils.print_with_colours("Architect: How many output models do you wish?")
        num_output_models = ""
        while (not utils.is_int(num_output_models)) or (int(num_output_models) < 1) or (int(num_output_models) > num_solns):
            num_output_models = utils.input_with_colours("Please specify a number between 1 and " + str(num_solns) + ". ")
            num_output_models = num_output_models.strip().upper()
            if num_output_models == "Q":
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                status_writer.close()
                exit()
        num_output_models = int(num_output_models)


    # Now, set up the script for model reconstruction.
    line_to_new_text = {}
    line_to_new_text[10] = "CPLEX_PATH=" + parameter_values["CPLEX_PATH"]
    line_to_new_text[11] = "FRAMED_PATH=" + parameter_values["FRAMED_PATH"]
    line_to_new_text[12] = "CARVEME_PATH=" + parameter_values["CARVEME_PATH"]

    line_to_new_text[16] = "MODEL_RECONSTRUCTION_PATH=" + architect_path + "/scripts/model_reconstruction"
    line_to_new_text[17] = "DATABASE=" + universe_set_of_reactions
    gapfill_script = parameter_values["CARVEME_PATH"] + "/scripts/gapfill"
    line_to_new_text[18] = "gapfill_script=" + gapfill_script

    line_to_new_text[21] = "ENZ_ANNOTATION_results=" + enzannot_results_file
    line_to_new_text[22] = "ADDITIONAL_ENZ_results=" + additional_preds_file

    line_to_new_text[25] = "USER_DEFINED_reactions=" + parameter_values["USER_def_reax"]

    line_to_new_text[28] = "OUTPUT_FOLDER=" + temp_folder
    line_to_new_text[29] = "OUTPUT_GAP_FILL=" + temp_folder + "/model_gapfilled_multi_" + str(num_solns) + ".lst"
    line_to_new_text[30] = "FINAL_OUTPUT_FOLDER=" + final_output_folder

    line_to_new_text[33] = "NUM_SOLNS=" + str(num_solns)
    line_to_new_text[34] = "NUM_OUTPUT_MODELS=" + str(num_output_models)

    get_high_conf_command = "python ${MODEL_RECONSTRUCTION_PATH}/0_get_high_conf_set_of_reactions_from_ec.py " + \
        "--ec_preds_file ${ENZ_ANNOTATION_results} --additional_preds_file ${ADDITIONAL_ENZ_results}" + \
            " --user_defined_file ${USER_DEFINED_reactions} --database ${DATABASE} --output_folder ${OUTPUT_FOLDER}" + \
                " --fasta_file " + parameter_values["SEQUENCE_FILE"]
    if min_num_high_conf != "":
        get_high_conf_command = get_high_conf_command + " --min_num_high_conf " + str(min_num_high_conf)
    if evalue_blastp is not None:
        get_high_conf_command = get_high_conf_command + " --evalue " + str(evalue_blastp) + " --blastfolder " + main_database_folder + "/model_reconstruction/Common_BiGG_info"
    get_high_conf_command = get_high_conf_command + " --warning_mets_to_include_file " + parameter_values["WARNING_mets"]
    line_to_new_text[40] = get_high_conf_command

    create_universe_set_rxns = "python ${MODEL_RECONSTRUCTION_PATH}/1_create_universe_set_of_reactions.py " + \
        "--database ${DATABASE} --output_folder ${OUTPUT_FOLDER} --warning_mets_to_include_file " + parameter_values["WARNING_mets"]
    line_to_new_text[42] = create_universe_set_rxns

    if penalty_deadend != "":
        new_create_scores_command = "python ${MODEL_RECONSTRUCTION_PATH}/2_create_reaction_scores_file.py " + \
            "--ec_preds_file ${ENZ_ANNOTATION_results} --database ${DATABASE} --output_folder ${OUTPUT_FOLDER} " +\
                "--penalty_exchange " + str(penalty_deadend)
        line_to_new_text[44] = new_create_scores_command

    perform_gap_fill_command = "python " + gapfill_script + " " + \
        temp_folder + "/SIMULATION_high_confidence_reactions_plus_essentials.xml -m M9 -o " + \
            temp_folder + "/model_gapfilled_multi_" + str(num_solns) + ".lst --scoredb " + \
                temp_folder + "/SIMULATION_reaction_scores.out " + \
                "--universe-file " + temp_folder + "/SIMULATED_reduced_universe_with_fva.xml " + \
                    "--pool-size ${NUM_SOLNS} --pool-gap " + str(pool_gap)
    if integrality_constraint != "":
        perform_gap_fill_command = perform_gap_fill_command + " --integrality-constraint " + str(integrality_constraint)
    line_to_new_text[49] = perform_gap_fill_command
    template_file = architect_path + "/scripts/model_reconstruction/TEMPLATE_run_reconstruction.sh"
    file_to_run = main_folder_with_recon_results + "/make_reconstruction.sh"
    utils.copy_and_replace(template_file, file_to_run, line_to_new_text)

    subprocess.call(["sh", file_to_run])
    status_writer.write("Step 5: " + str(datetime.datetime.now()) + ": Gap-filling done.\n")

    status_writer.close()
    utils.print_with_colours("Architect: Thank you for using our tool today! Reconstruction is now done. Find your results under: " + final_output_folder)