import subprocess

# Some key messages to be written to the status file
ABOUT_TO_RUN_ENZ_TOOL="Architect about to run the individual tools specified above."
ALREADY_RAN_ENZ_TOOL="User has specified that they already have results from individual tools so these will not be run de novo"
TERMINATION="User wants to quit so Architect will exit now."


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
            parameter = line[:16].strip()
            value = line[16:].strip()
            parameter_values[parameter] = value

    check_parameters_loaded(parameter_values)
    return parameter_values


def check_parameters_loaded(parameter_values):

    acceptable_params = ["BLAST_DIR", "CATFAM_DIR", "EMBOSS_DIR", "DETECT_DIR", "EFICAz_DIR", "EnzDP_DIR", "PRIAM_DIR", "DATABASE", "SEQUENCE_FILE"]
    if len(parameter_values) != len(acceptable_params):
        raise Exception("Architect: Missing parameter values. Please verify all parameters are defined in sample_run.tsv.")
    for param in acceptable_params:
        if param not in parameter_values:
            raise Exception("Architect: Invalid parameter values specified. Please verify parameters defined in sample_run.tsv.")


def get_shell_to_python_readable_location(shell_variable):
    """The shell variable needs to be written as in shell."""

    cmd = 'echo ' + shell_variable
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
    return p.stdout.readlines()[0].strip()