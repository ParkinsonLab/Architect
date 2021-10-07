import subprocess
import os

# Some key messages to be written to the status file
ABOUT_TO_RUN_ENZ_TOOL="Architect about to run the individual tools specified above."
ALREADY_RAN_ENZ_TOOL="User has specified that they already have results from individual tools so these will not be run de novo"
TERMINATION="User wants to quit so Architect will exit now."


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    ENDC = '\033[0m'


def print_with_colours(string, colour=bcolors.HEADER):

    print(colour + string + bcolors.ENDC)


def print_warning(string):

    print_with_colours(string, bcolors.GREEN)


def copy_and_replace(original_file_name, new_file_name, line_to_new_text):

    with open(original_file_name) as input_file:
        with open(new_file_name, "w") as writer:
            for i, line in enumerate(input_file):
                if (i+1) in line_to_new_text:
                    new_text = line_to_new_text[i+1]
                    writer.write(new_text + "\n")
                else:
                    writer.write(line)

                    
def is_message_present(status_file, str_of_int):

    with open(status_file) as open_file:
        for line in open_file:
            line = line.strip()
            if str_of_int in line:
                open_file.close()
                return True
    return False

def user_has_quit(status_file):

    return is_message_present(status_file, TERMINATION)


def just_ran_tools(status_file):

    return is_message_present(status_file, ABOUT_TO_RUN_ENZ_TOOL)


def read_parameter_values(file_name):

    parameter_values = {}
    with open(file_name) as open_file:
        for i, line in enumerate(open_file):
            line = line.strip()
            if (i == 0) or (line == ""):
                continue
            parameter = line.split()[0]
            value = line[len(parameter):].strip()
            # parameter = line[:16].strip()
            # value = line[16:].strip()
            parameter_values[parameter] = value

    check_parameters_loaded(parameter_values)
    return parameter_values


def check_parameters_loaded(parameter_values):

    acceptable_params = ["BLAST_DIR", "CATFAM_DIR", "EMBOSS_DIR", "DETECT_DIR", "EFICAz_DIR", "EnzDP_DIR", "PRIAM_DIR", "PRIAM_db", "DATABASE", \
        "SEQUENCE_FILE", "USER_def_reax", "CPLEX_PATH", "FRAMED_PATH", "CARVEME_PATH", "WARNING_mets"]
    if len(parameter_values) != len(acceptable_params):
        raise Exception("Architect: Missing parameter values. Please verify all parameters are defined in sample_run.tsv.")
    for param in acceptable_params:
        if param not in parameter_values:
            raise Exception("Architect: Invalid parameter values specified. Please verify parameters defined in sample_run.tsv.")


def get_shell_to_python_readable_location(shell_variable):
    """The shell variable needs to be written as in shell."""

    cmd = 'echo ' + shell_variable
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
    answer = p.stdout.readlines()[0].strip()
    if type(answer) == type("string"):
        return answer
    else: #byte
        return answer.decode('utf-8')


def is_float(string):
    """Can the string be converted to a floating point number?"""

    try:
        float(string)
        return True
    except:
        return False


def is_int(string):
    """Can the string be converted to a floating point number?"""

    try:
        int(string)
        return True
    except:
        return False


def check_info_set_up(filename, message):

    if not os.path.isfile(filename):
        return False
    answer = False
    with open(filename) as open_file:
        for line in open_file:
            line = line.strip()
            if line == "":
                continue
            if message in line:
                answer = True
    return answer