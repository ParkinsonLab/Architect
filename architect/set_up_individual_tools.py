# Under construction.
import math
from argparse import ArgumentParser
import sys, os

def read_parameter_values(file_name):

    parameter_values = {}
    with open(file_name) as open_file:
        for i, line in enumerate(open_file):
            line = line.strip()
            if (i == 0) or (line == ""):
                continue
            parameter = line[:16].strip()
            value = line[16:].strip()
            parameter_values[parameter] = value

    check_parameters_loaded(parameter_values)
    return parameter_values


def check_parameters_loaded(parameter_values):

    acceptable_params = ["BLAST_DIR", "CATFAM_DIR", "EMBOSS_DIR", "DETECT_DIR", "EFICAz_DIR", "EnzDP_DIR", "PRIAM_DIR", "SEQUENCE_FILE"]
    if len(parameter_values) != len(acceptable_params):
        raise Exception("Architect: Missing parameter values. Please verify all parameters are defined in sample_run.tsv.")
    for param in acceptable_params:
        if param not in parameter_values:
            raise Exception("Architect: Invalid parameter values specified. Please verify parameters defined in sample_run.tsv.")


def determine_num_to_split(sequence_file):

    tool_to_num_split = {}
    k_to_split = {}
    num_seqs = count_num_of_seqs(sequence_file)

    # Print recommended to user and ask if they accept.
    accept, tool_to_num_split = print_recommended(num_seqs)

    # Otherwise, iterate until user specifies what they want.
    if not accept:
        for tool_name in ["CatFam", "EFICAz", "EnzDP"]:
            k = 1
            answer = ""
            while answer != "Y":
                num_files = 40 * k
                suggested = math.ceil(num_seqs/(num_files))
                if ((num_files + 40) > num_seqs):
                    if (num_files <= num_seqs):
                        print ("Architect: Warning: splitting into more than " + str(num_files) + " files may lead to unexpected behaviour.")
                    else:
                        print ("Architect: Warning: splitting into " + str(num_files) + " files may lead to unexpected behaviour.")
                answer = input("Architect: For " + tool_name + ", split sequences into " + str(num_files) + " files with at most " \
                    + str(suggested) + " sequences? [y/n]: ")
                answer = answer.strip().upper()
                if answer == "N":
                    k += 1

            if k not in k_to_split:
                current_split = get_num_seqs_per_file(num_seqs, k)
                tool_to_num_split[tool_name] = current_split
                k_to_split[k] = current_split
            else:
                tool_to_num_split[tool_name] = k_to_split[k]
                
    return tool_to_num_split


def print_recommended(num_seqs):

    accept = False
    tool_to_num_split = {}
    #TODO: recommended for CatFam
    # catfam_recommended = 
    #TODO: recommended for EFICAz
    #TODO: recommended for EnzDP
    return accept, tool_to_num_split


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
            

def customize_catfam(parameter_values, project_name, current_working_directory, i_to_num_split):

    current_folder = project_name + "/CatFam"
    os.mkdir(current_folder)
    num_to_new_line = {}
    num_to_new_line[4] = "#SBATCH --job-name=CatFam_" + project_name
    num_to_new_line[7] = "PATH=$PATH:" + parameter_values["BLAST_DIR"]
    num_to_new_line[10] = "cd " + current_working_directory + "/" + project_name + "/CatFam"
    num_to_new_line[13] = "CATFAM_DIR=" + parameter_values["CATFAM_DIR"]
    copy_and_replace("scripts/individual_enzyme_annotation/CatFam/run_catfam.sh", \
        current_folder + "/run_catfam.sh", num_to_new_line)

    os.mkdir(current_folder + "/Split_seqs")
    write_split_seqs(current_folder + "/Split_seqs", i_to_num_split, parameter_values["SEQUENCE_FILE"])


def customize_detect(parameter_values, project_name, current_working_directory):
    
    current_folder = project_name + "/DETECT"
    os.mkdir(current_folder)
    num_to_new_line = {}
    num_to_new_line[4] = "#SBATCH --job-name=DETECT_" + project_name
    num_to_new_line[7] = "DETECT_TOOL=" + parameter_values["DETECT_DIR"] + "/detect_2.2.7.py"
    num_to_new_line[10] = "export PATH=" + parameter_values["DETECT_DIR"] + "/:$PATH"
    num_to_new_line[11] = "export PATH=" + parameter_values["EMBOSS_DIR"] + ":$PATH"
    num_to_new_line[21] = "cd " + current_working_directory + "/" + project_name + "/DETECT"
    num_to_new_line[27] = "SEQ_NAME=../../" + parameter_values["SEQUENCE_FILE"]
    copy_and_replace("scripts/individual_enzyme_annotation/CatFam/run_detect.sh", \
        current_folder + "/run_detect.sh", num_to_new_line)


def customize_eficaz(parameter_values, project_name, current_working_directory, i_to_num_split):

    current_folder = project_name + "/EFICAz"
    os.mkdir(current_folder)
    copy_and_replace("scripts/individual_enzyme_annotation/EFICAz/individualize.sh", current_folder + "/individualize.sh", {})

    num_to_new_line = {}
    num_to_new_line[4] = "#SBATCH --job-name=EFICAz_" + project_name + "_SEQUENCE_FILENAME_X1"
    num_to_new_line[7] = "EFICAz25_PATH=" + parameter_values["EFICAz_DIR"]
    num_to_new_line[13] = "cd " + current_working_directory + "/" + project_name + "/EFICAz"
    num_to_new_line[104] = "\tmy_scratch=" + current_working_directory + "/" + project_name + "/EFICAz/Results"
    copy_and_replace("scripts/individual_enzyme_annotation/EFICAz/TEMPLATE_eficaz.sh", \
        current_folder + "/TEMPLATE_eficaz.sh", num_to_new_line)

    os.mkdir(current_folder + "/Split_seqs")
    write_split_seqs(current_folder + "/Split_seqs", i_to_num_split, parameter_values["SEQUENCE_FILE"])


def customize_enzdp(parameter_values, project_name, current_working_directory, i_to_num_split):

    current_folder = project_name + "/EnzDP"
    os.mkdir(current_folder)
    copy_and_replace("scripts/individual_enzyme_annotation/EnzDP/individualize.sh", current_folder + "/individualize.sh", {})
    copy_and_replace("scripts/individual_enzyme_annotation/EnzDP/TEMPLATE_project.py", current_folder + "/TEMPLATE_project.py", {})
    
    num_to_new_line = {}
    num_to_new_line[4] = "#SBATCH --job-name=EnzDP_" + project_name
    num_to_new_line[7] = "ENZDP_TOOL=" + parameter_values["EnzDP_DIR"]
    num_to_new_line[11] = "folder=" + current_working_directory + "/" + project_name + "/EnzDP"
    copy_and_replace("scripts/individual_enzyme_annotation/EnzDP/run_enzdp.sh", current_folder + "/run_enzdp.sh", num_to_new_line)

    os.mkdir(current_folder + "/Split_seqs")
    write_split_seqs(current_folder + "/Split_seqs", i_to_num_split, parameter_values["SEQUENCE_FILE"])


def customize_priam(parameter_values, project_name, current_working_directory):

    current_folder = project_name + "/PRIAM"
    os.mkdir(current_folder)

    num_to_new_line = {}
    num_to_new_line[4] = "#SBATCH --job-name=PRIAM_" + project_name
    num_to_new_line[7] = "my_WORKDIR=" + current_working_directory + "/" + project_name + "/PRIAM"
    num_to_new_line[8] = "TEST=" + parameter_values["SEQUENCE_FILE"]
    num_to_new_line[9] = "PRIAM_SEARCH=" + parameter_values["PRIAM_DIR"]
    num_to_new_line[21] = "BLAST_BIN=" + parameter_values["BLAST_DIR"]
    copy_and_replace("scripts/individual_enzyme_annotation/PRIAM/run_priam.sh", current_folder + "/run_priam.sh", num_to_new_line)


def copy_and_replace(original_file_name, new_file_name, line_to_new_text):

    with open(original_file_name) as input_file:
        with open(new_file_name, "w") as writer:
            for i, line in enumerate(input_file):
                if (i+1) in line_to_new_text:
                    new_text = line_to_new_text[i]
                    writer.write(new_text + "\n")
                else:
                    writer.write(line)


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
                if curr_num_seqs >= i_to_num_split[i]:
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
    args = parser.parse_args()
    arguments_file = args.arguments_file
    project_name = args.project_name

    # If the folder already exists, throw an exception.
    if os.path.isdir(project_name):
        raise Exception("Architect: Please specify a different project name.  Corresponding directory already exists.")
    os.mkdir(project_name)

    parameter_values = read_parameter_values(arguments_file)
    tool_to_num_split = determine_num_to_split(parameter_values["SEQUENCE_FILE"])

    customize_catfam(parameter_values, project_name, current_working_directory, tool_to_num_split["CatFam"])
    customize_detect(parameter_values, project_name, current_working_directory)
    customize_eficaz(parameter_values, project_name, current_working_directory, tool_to_num_split["EFICAz"])
    customize_enzdp(parameter_values, project_name, current_working_directory, tool_to_num_split["EnzDP"])
    customize_priam(parameter_values, project_name, current_working_directory)
