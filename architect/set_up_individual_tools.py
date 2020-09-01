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

    if len(parameter_values) != 9:
        raise Exception("Missing parameter values. Please verify all parameters are defined in sample_run.tsv.")
    for param in ["PROJECT_NAME", "BLAST_DIR", "CATFAM_DIR", "EMBOSS_DIR", "DETECT_DIR", "EFICAz_DIR", "EnzDP_DIR", "PRIAM_DIR", "SEQUENCE_FILE"]:
        if param not in parameter_values:
            raise Exception("Invalid parameter values specified. Please verify parameters defined in sample_run.tsv.")


def determine_num_to_split(sequence_file):

    tool_to_num_split = {}
    num_seqs = count_num_of_seqs(sequence_file)
    for tool_name in ["CatFam", "EFICAz", "EnzDP"]:
        k = 1
        answer = ""
        while answer != "Y":
            num_files = 40 * k
            suggested = math.ceil(num_seqs/40)
            answer = input("Architect: For " + tool_name + ", split sequences into " + str(num_files) + " files with at most " \
                + str(suggested) + " sequences? [y/n]: ")
            answer = answer.strip().upper()
            if answer == "N":
                k += 1
        tool_to_num_split[tool_name] = suggested
    return tool_to_num_split


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
            

def customize_catfam(parameter_values):

    return 


def customize_detect(parameter_values):
    
    return


def customize_eficaz(parameter_values):

    return


def customize_enzdp(parameter_values):

    return


def customize_priam(parameter_values):

    return


if __name__ == '__main__':

    sys.path.append(os.getcwd())
    print (os.getcwd())

    try:
        input = raw_input
    except NameError:
        pass

    parser = ArgumentParser(description="Sets up the scripts for the individual enzyme annotation tools.")
    parser.add_argument("--arguments_file", type=str, help="File with the values of the parameters.", required=True)
    args = parser.parse_args()
    arguments_file = args.arguments_file

    parameter_values = read_parameter_values(arguments_file)
    catfam_num_split, eficaz_num_split, enzdp_num_split = determine_num_to_split(parameter_values["SEQUENCE_FILE"])

    customize_catfam(parameter_values)
    customize_detect(parameter_values)
    customize_eficaz(parameter_values)
    customize_enzdp(parameter_values)
    customize_priam(parameter_values)
