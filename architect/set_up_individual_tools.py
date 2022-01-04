# Under construction.
import math
from argparse import ArgumentParser
import sys, os
import subprocess
import shutil
import datetime
import utils


def determine_tools_to_run_docker(status_writer):

    tools_to_run = []
    exclude_tools = []
    for tool_name in ["CatFam", "DETECT", "EFICAz", "EnzDP", "PRIAM"]:
        answer = ""
        while answer not in ["Y", "N", "Q"]:
            answer = utils.input_with_colours("Architect: Run " + tool_name + "? [y/n] ")
            answer = answer.strip().upper()
        if answer == "Y":
            tools_to_run.append(tool_name)
        elif answer == "N":
            exclude_tools.append(tool_name)
        elif answer == "Q":
            status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
            exit()
    return tools_to_run, exclude_tools


def customize_docker_run(tool_of_int):

    utils.copy_files_recursively("/tools/Architect/scripts/individual_enz_annot_docker/" + tool_of_int, "/architect_run/organism/" + tool_of_int)


def determine_num_to_split(sequence_file, status_writer):

    exclude_tools = []
    tool_to_num_split = {}
    k_to_split = {}
    num_seqs = count_num_of_seqs(sequence_file)

    # Get recommended information.
    rec_tool_to_num_split, rec_tool_to_max_seqs, rec_tool_to_time = get_recommended_overall(num_seqs)

    # Otherwise, iterate until user specifies what they want.
    for tool_name in ["CatFam", "DETECT", "EFICAz", "EnzDP", "PRIAM"]:
        rec_num_split = rec_tool_to_num_split[tool_name]
        rec_num_files = rec_num_split * 40
        rec_max_seq = int(rec_tool_to_max_seqs[tool_name])
        rec_time = rec_tool_to_time[tool_name]

        if tool_name in ["DETECT", "PRIAM"]:
            answer = utils.input_with_colours("Architect: for " + tool_name + ", sequences will not be split and job will run for maximum " + \
                str(rec_time) + " hours.\n" +\
                    "Customizations to be made separately by user. Press enter to continue, or [x] to exclude this tool.\n")
            if answer.strip().upper() == "X":
                exclude_tools.append(tool_name)
            if answer.strip().upper() == "Q":
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                exit()
            continue

        # Check user input only for CatFam, EFICAz and EnzDP.
        accept = False
        answer = ""
        while answer not in ["Y", "N"]:
            answer = utils.input_with_colours("Architect: Recommends that for " + tool_name + ", split sequences into " + str(rec_num_files) + \
                " files with at most " + str(rec_max_seq) + " sequences, for maximum running time of " + str(rec_time) + " hours." +\
                    "\nAccept? [y/n].  Alternately, enter [x] to exclude this tool:\n")
            answer = answer.strip().upper()
            if answer == "X":
                exclude_tools.append(tool_name)
                break
            if answer == "Q":
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                exit()
        if answer == "X":
            continue
        
        accept = (answer == "Y")

        if accept:
            k = rec_num_split

        else:
            k = 1
            answer = ""
            while answer != "Y":
                if (k == rec_num_split):
                    k += 1
                    continue
                num_files = 40 * k
                suggested = int(math.ceil(num_seqs/(num_files * 1.0)))
                if ((num_files + 40) > num_seqs):
                    if (num_files <= num_seqs):
                        utils.print_warning ("Architect: Warning: splitting into more than " + str(num_files) + " files may lead to unexpected behaviour.")
                    else:
                        utils.print_warning ("Architect: Warning: splitting into " + str(num_files) + " files may lead to unexpected behaviour.")
                answer = utils.input_with_colours("Architect: For " + tool_name + ", split sequences into " + str(num_files) + " files with at most " \
                    + str(suggested) + " sequences for maximum running time of " + str(rec_time) + " hours? [y/n]. " \
                        + "Alternately, enter [x] to exclude this tool:\n")
                answer = answer.strip().upper()
                if answer == "N":
                    k += 1
                elif answer == "X":
                    exclude_tools.append(tool_name)
                    break
                elif answer == "Q":
                    status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                    exit()

            if answer == "X":
                continue

        if k not in k_to_split:
            current_split = get_num_seqs_per_file(num_seqs, k)
            tool_to_num_split[tool_name] = current_split
            k_to_split[k] = current_split
        else:
            tool_to_num_split[tool_name] = k_to_split[k]
    return tool_to_num_split, rec_tool_to_time["DETECT"], rec_tool_to_time["PRIAM"], exclude_tools


def get_recommended_per_tool(num_seqs, max_num_per_file):

    k = 1
    num_files = 40.0 * k
    num_seqs_per_file = int(math.ceil(num_seqs/(num_files * 1.0)))
    while num_seqs_per_file > max_num_per_file:
        k += 1
        num_files = 40.0 * k
        num_seqs_per_file = math.ceil(num_seqs/(num_files))
    return k, num_seqs_per_file


def get_recommended_overall(num_seqs):

    catfam_k, catfam_num_seqs = get_recommended_per_tool(num_seqs, 5000)
    eficaz_k, eficaz_num_seqs = get_recommended_per_tool(num_seqs, 180)
    enzdp_k, enzdp_num_seqs = get_recommended_per_tool(num_seqs, 1800)

    # For CatFam, EFICAz and EnzDP, divisions are likely performed.
    tool_to_num_split, tool_to_max_seqs, tool_to_time = {}, {}, {}

    tool_to_num_split["CatFam"] = catfam_k
    tool_to_num_split["EFICAz"] = eficaz_k
    tool_to_num_split["EnzDP"] = enzdp_k

    tool_to_max_seqs["CatFam"] = catfam_num_seqs
    tool_to_max_seqs["EFICAz"] = eficaz_num_seqs
    tool_to_max_seqs["EnzDP"] = enzdp_num_seqs

    tool_to_time["CatFam"] = 3
    tool_to_time["EFICAz"] = 12
    tool_to_time["EnzDP"] = 3

    # For DETECT and PRIAM, implementations involve some kind of parallelization.
    # Check the number of sequences to ensure that we are more or less sure that jobs will finish on time.
    if num_seqs <= 30000:
        tool_to_time["DETECT"] = 12
    else:
        tool_to_time["DETECT"] = 24

    if num_seqs <=40000:
        tool_to_time["PRIAM"] = 3
    else:
        k = 1
        while num_seqs > 40000 * k:
            k += 1
        tool_to_time["PRIAM"] = 3 * k
        
    tool_to_num_split["DETECT"] = 0
    tool_to_max_seqs["DETECT"] = num_seqs
    tool_to_num_split["PRIAM"] = 0
    tool_to_max_seqs["PRIAM"] = num_seqs

    return tool_to_num_split, tool_to_max_seqs, tool_to_time


def get_num_seqs_per_file(num_seqs, k):

    file_index_to_num = {}
    lower_bound = math.floor(num_seqs / (40 * k))

    total_placed_seqs = 0
    num_files = 40 * k
    i = 0

    # First, place sequences equally into all files.
    while (i < num_files): 
        # In case the user has specified more files than there are sequences, despite warnings.
        if total_placed_seqs >= num_seqs: 
            file_index_to_num[i] = 0
        else:
            file_index_to_num[i] = lower_bound
            total_placed_seqs += lower_bound
        i += 1

    # Now, add extra sequences into files (number not divisible by 40*k).
    while (total_placed_seqs < num_seqs):
        i = 0
        while (i < num_files) and (total_placed_seqs < num_seqs):
            file_index_to_num[i] += 1
            total_placed_seqs += 1
            i += 1
 
    return file_index_to_num


def count_num_of_seqs(sequence_file):

    num_seqs = 0
    with open(sequence_file) as open_file:
        for line in open_file:
            line = line.strip()
            if line == "":
                continue
            if line[0] == ">":
                num_seqs += 1
    return num_seqs
            

def mkdir_if_not_exists(folder, delete_if_exists=False):

    if not os.path.isdir(folder):
        os.mkdir(folder)
    else:
        if delete_if_exists:
            shutil.rmtree(folder)
            os.mkdir(folder)


def customize_catfam(architect_location, parameter_values, project_name, output_dir, i_to_num_split):

    current_folder = output_dir + "/" + project_name + "/CatFam"
    mkdir_if_not_exists(current_folder)
    num_to_new_line = {}
    num_to_new_line[4] = "#SBATCH --job-name=CatFam_" + project_name
    num_to_new_line[7] = "PATH=$PATH:" + parameter_values["BLAST_DIR"]
    num_to_new_line[10] = "cd " + current_folder
    num_to_new_line[13] = "CATFAM_DIR=" + parameter_values["CATFAM_DIR"]
    utils.copy_and_replace(architect_location + "/scripts/individual_enzyme_annotation/CatFam/run_catfam.sh", \
        current_folder + "/run_catfam.sh", num_to_new_line)

    mkdir_if_not_exists(current_folder + "/Split_seqs", True)
    write_split_seqs(current_folder + "/Split_seqs", i_to_num_split, parameter_values["SEQUENCE_FILE"])


def customize_detect(architect_location, parameter_values, project_name, output_dir, time):
    
    current_folder = output_dir + "/" + project_name + "/DETECT"
    mkdir_if_not_exists(current_folder)
    num_to_new_line = {}
    num_to_new_line[3] = "#SBATCH --time=" + str(time) + ":00:00"
    num_to_new_line[4] = "#SBATCH --job-name=DETECT_" + project_name
    num_to_new_line[7] = "DETECT_TOOL=" + parameter_values["DETECT_DIR"] + "/detect_2.2.7.py"
    num_to_new_line[10] = "export PATH=" + parameter_values["DETECT_DIR"] + "/:$PATH"
    num_to_new_line[11] = "export PATH=" + parameter_values["EMBOSS_DIR"] + "/:$PATH"
    num_to_new_line[22] = "cd " + current_folder
    num_to_new_line[28] = "SEQ_NAME=" + parameter_values["SEQUENCE_FILE"]
    utils.copy_and_replace(architect_location + "/scripts/individual_enzyme_annotation/DETECT/run_detect.sh", \
        current_folder + "/run_detect.sh", num_to_new_line)


def customize_eficaz(architect_location, parameter_values, project_name, output_dir, i_to_num_split):

    current_folder = output_dir + "/" + project_name + "/EFICAz"
    mkdir_if_not_exists(current_folder)
    utils.copy_and_replace(architect_location + "/scripts/individual_enzyme_annotation/EFICAz/individualize.sh", current_folder + "/individualize.sh", {})

    num_to_new_line = {}
    num_to_new_line[4] = "#SBATCH --job-name=EFICAz_" + project_name + "_SEQUENCE_FILENAME_X1"
    num_to_new_line[7] = "EFICAz25_PATH=" + parameter_values["EFICAz_DIR"]
    num_to_new_line[14] = "cd " + current_folder
    num_to_new_line[105] = "\tmy_scratch=" + current_folder + "/Results"
    utils.copy_and_replace(architect_location + "/scripts/individual_enzyme_annotation/EFICAz/TEMPLATE_eficaz.sh", \
        current_folder + "/TEMPLATE_eficaz.sh", num_to_new_line)

    mkdir_if_not_exists(current_folder + "/Split_seqs", True)
    write_split_seqs(current_folder + "/Split_seqs", i_to_num_split, parameter_values["SEQUENCE_FILE"])


def customize_enzdp(architect_location, parameter_values, project_name, output_dir, i_to_num_split):

    current_folder = output_dir + "/" + project_name + "/EnzDP"
    mkdir_if_not_exists(current_folder)
    utils.copy_and_replace(architect_location + "/scripts/individual_enzyme_annotation/EnzDP/individualize_project.sh", current_folder + "/individualize_project.sh", {})

    num_to_new_line = {}
    num_to_new_line[3] = "FASTA_FILE='" + current_folder + "/Split_seqs/SEQ_NAME'"
    num_to_new_line[5] = "OUTPUT_FILE='" + current_folder + "/Results/SEQ_NAME.out'"
    utils.copy_and_replace(architect_location + "/scripts/individual_enzyme_annotation/EnzDP/TEMPLATE_project.py", current_folder + "/TEMPLATE_project.py", num_to_new_line)
    
    num_to_new_line = {}
    num_to_new_line[4] = "#SBATCH --job-name=EnzDP_" + project_name
    num_to_new_line[7] = "ENZDP_TOOL=" + parameter_values["EnzDP_DIR"]
    num_to_new_line[11] = "folder=" + current_folder
    utils.copy_and_replace(architect_location + "/scripts/individual_enzyme_annotation/EnzDP/run_enzdp.sh", current_folder + "/run_enzdp.sh", num_to_new_line)

    mkdir_if_not_exists(current_folder + "/Split_seqs", True)
    write_split_seqs(current_folder + "/Split_seqs", i_to_num_split, parameter_values["SEQUENCE_FILE"])


def customize_priam(architect_location, parameter_values, project_name, output_dir, time):

    current_folder = output_dir + "/" + project_name + "/PRIAM"
    mkdir_if_not_exists(current_folder)

    num_to_new_line = {}
    num_to_new_line[3] = "#SBATCH --time=" + str(time) + ":00:00"
    num_to_new_line[4] = "#SBATCH --job-name=PRIAM_" + project_name
    num_to_new_line[7] = "my_WORKDIR=" + current_folder
    num_to_new_line[8] = "TEST=" + parameter_values["SEQUENCE_FILE"]
    num_to_new_line[9] = "PRIAM_SEARCH=" + parameter_values["PRIAM_DIR"]
    num_to_new_line[10] = "PRIAM_profiles_library=" + parameter_values["PRIAM_db"]
    num_to_new_line[22] = "BLAST_BIN=" + parameter_values["BLAST_DIR"]
    utils.copy_and_replace(architect_location + "/scripts/individual_enzyme_annotation/PRIAM/run_priam.sh", current_folder + "/run_priam.sh", num_to_new_line)


def write_split_seqs(folder_name, i_to_num_split, sequence_file):

    i = 0
    with open(sequence_file) as open_file:
        writer = open(folder_name + "/SEQ_" + str(i) + ".fa", "w")
        curr_num_seqs = 0
        for line in open_file:
            line = line.strip()
            if line == "":
                continue
            if line[0] == ">":
                curr_num_seqs += 1
                if curr_num_seqs > i_to_num_split[i]:
                    curr_num_seqs = 1
                    i += 1
                    writer.close()
                    writer = open(folder_name + "/SEQ_" + str(i) + ".fa", "w") 
            writer.write(line + "\n")


if __name__ == '__main__':

    current_working_directory = os.getcwd()
    sys.path.append(current_working_directory)

    try:
        input = raw_input
    except NameError:
        pass

    parser = ArgumentParser(description="Sets up the scripts for the individual enzyme annotation tools.")
    parser.add_argument("--arguments_file", type=str, help="File with the values of the parameters.", required=True)
    parser.add_argument("--project_name", type=str, help="Name of the project (eg: organism name).", required=True)
    parser.add_argument("--output_dir", type=str, help="Location of project directory (default: current working directory).", required=False, default=current_working_directory)
    parser.add_argument("--architect_path", type=str, help="Location of Architect project directory", required=True)
    parser.add_argument("--i", type=str, help="Specifies if running outside of Docker if and only if True.", \
        choices=["yes", "no"], default="yes")

    args = parser.parse_args()
    arguments_file = args.arguments_file
    output_dir = args.output_dir
    project_name = args.project_name
    architect_location = args.architect_path
    within_docker = (args.i == "no")

    parameter_values = utils.read_parameter_values(arguments_file)

    utils.print_with_colours("Welcome to Architect! It's a beautiful day for metabolic model reconstruction!")
    utils.print_with_colours("Friendly note: Enter [q] at any point where user input is required to exit Architect.")

    utils.print_with_colours("Architect: Now, we will try to procure results from individual enzyme annotation tools.")
    
    # If the folder already exists, warn the user about it, and make sure they want to continue.
    if os.path.isdir(output_dir + "/" + args.project_name):
        status_writer = open(output_dir + "/" + args.project_name + "/architect_status.out", "w")
        status_writer.write("Begin:" + str(datetime.datetime.now()) + ": Architect has started.\n")
        status_writer.close()

        answer = ""
        while answer != "Y":
            answer = utils.input_with_colours("Architect: Project directory already exists. \n" + \
                "Type [y] to continue; existing subdirectories in directory may be modified. ")
            answer = answer.strip().upper()
            if answer == "Q":
                status_writer = open(output_dir + "/" + args.project_name + "/architect_status.out", "a")
                status_writer.write("Begin:" + str(datetime.datetime.now()) + ": Architect has started.")
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                status_writer.close()
                exit()
    else:
        os.mkdir(output_dir + "/" + args.project_name)
        status_writer = open(output_dir + "/" + args.project_name + "/architect_status.out", "w")
        status_writer.write("Begin:" + str(datetime.datetime.now()) + ": Architect has started.\n")
        status_writer.close()

    status_writer = open(output_dir + "/" + args.project_name + "/architect_status.out", "a")

    # Have the classifiers already been set up?  If not, ask the user if they want to proceed.
    enzyme_annotation_db_folder = utils.get_shell_to_python_readable_location(parameter_values["DATABASE"]) + "/enzyme_annotation"
    classifier_set_up_status_file = enzyme_annotation_db_folder + "/classifier_set_up.out"
    if not utils.check_info_set_up(classifier_set_up_status_file, "Successfully set up all classifiers"):
        answer = ""
        while answer != "Y":
            answer = utils.input_with_colours("Architect: We have detected that the classifiers have yet to be set up.  \
                \nArchitect: This is an essential step for running Architect. Enter [y] to proceed. Otherwise, quit by entering [n]: ")
            answer = answer.strip().upper()

            if answer in ["Q", "N"]:
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                status_writer.close()
                utils.print_with_colours("Architect will now exit.")
                exit()

        status_writer.write("Set up:" + str(datetime.datetime.now()) + ": Classifiers about to be set up.\n")
        utils.print_with_colours("Architect: Classifiers will now be set up.  This will take some time.")

        # Only if using Docker do we download the Database here.
        if within_docker:
            subprocess.call(["sh", "/tools/Architect/Docker_run_specific/set_up_architect_db.sh"])

        set_up_command = ["python", architect_location + "/scripts/ensemble_enzyme_annotation/x_set_up_classifiers.py"]
        set_up_command.append("-t")
        set_up_command.append(enzyme_annotation_db_folder)
        set_up_command.append("-s")
        set_up_command.append(classifier_set_up_status_file)
        subprocess.call(set_up_command)
        status_writer.write("Set up:" + str(datetime.datetime.now()) + ": Classifier set up is complete.\n")
        utils.print_with_colours("Architect: Classifier set up complete.")

    answer = ""
    while answer not in ["N", "Y", "Q"]:
        answer = utils.input_with_colours("Architect: Do you need to run any individual enzyme annotation tools? Reply 'n' if you already have the raw results. [y/n] ")
        answer = answer.strip().upper()
    if answer == "N":
        status_writer.write("Step1/2:" + str(datetime.datetime.now()) + ": " + utils.ALREADY_RAN_ENZ_TOOL + "\n")
        status_writer.close()
        exit()
    if answer == "Q":
        status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
        status_writer.close()
        exit()

    parameter_values["SEQUENCE_FILE"] = utils.get_shell_to_python_readable_location(parameter_values["SEQUENCE_FILE"])
    if not within_docker:
        tool_to_num_split, detect_time, priam_time, exclude_tools = determine_num_to_split(parameter_values["SEQUENCE_FILE"], status_writer)
    else:
        tools_to_run, exclude_tools = determine_tools_to_run_docker(status_writer)

    num_tools = str(5 - len(exclude_tools))
    status_writer.write("Step_1:" + str(datetime.datetime.now()) + ": Architect started setting up scripts for running the following " + num_tools + " individual enzyme annotation tools.\n")
    if not within_docker:
        if "CatFam" not in exclude_tools:
            customize_catfam(architect_location, parameter_values, project_name, output_dir, tool_to_num_split["CatFam"])
            status_writer.write("\tTool_of_interest:CatFam\n")
        if "DETECT" not in exclude_tools:
            customize_detect(architect_location, parameter_values, project_name, output_dir, detect_time)
            status_writer.write("\tTool_of_interest:DETECT\n")
        if "EFICAz" not in exclude_tools:
            customize_eficaz(architect_location, parameter_values, project_name, output_dir, tool_to_num_split["EFICAz"])
            status_writer.write("\tTool_of_interest:EFICAz\n")
        if "EnzDP" not in exclude_tools:
            customize_enzdp(architect_location, parameter_values, project_name, output_dir, tool_to_num_split["EnzDP"])
            status_writer.write("\tTool_of_interest:EnzDP\n")
        if "PRIAM" not in exclude_tools:
            customize_priam(architect_location, parameter_values, project_name, output_dir, priam_time)
            status_writer.write("\tTool_of_interest:PRIAM\n")
    else:
        for tool_of_int in tools_to_run:
            customize_docker_run(tool_of_int)
            status_writer.write("\tTool_of_interest:" + tool_of_int + "\n")
    status_writer.close()