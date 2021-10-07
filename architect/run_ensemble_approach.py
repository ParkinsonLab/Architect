import os
import sys
from argparse import ArgumentParser
import datetime
import subprocess
import utils

if __name__ == '__main__':

    current_working_directory = os.getcwd()
    sys.path.append(current_working_directory)

    try:
        input = raw_input
    except NameError:
        pass

    parser = ArgumentParser(description="Runs the scripts for the individual enzyme annotation tools.")
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

    status_file = output_dir + "/" + args.project_name + "/architect_status.out"
    
    # First verify that the user has not quit.
    if utils.user_has_quit(status_file) or utils.just_ran_tools(status_file):
        exit()

    status_writer = open(status_file, "a")

    main_folder_with_results = output_dir +  "/" + project_name + "/Ensemble_annotation_files"

    # If the folder with ensemble results does not exist yet, carry on.
    # Otherwise, ask the user if they want to proceed with ensemble enzyme annotation or not.
    if os.path.isdir(main_folder_with_results + "/Ensemble_results"):
        answer = ""
        while answer not in ["Y", "N"]:
            answer = utils.input_with_colours("Architect: We have detected that you have run an ensemble method already.\nDo you wish to run another ensemble method? [y/n] ")
            answer = answer.strip().upper()
            if answer == "Q":
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                status_writer.close()
                exit() 
        if answer == "N":
            status_writer.write("Step_4: " + str(datetime.datetime.now()) + ": Ensemble method has been previously run. User does not wish to run another.\n")
            exit()
    else:
        os.mkdir(main_folder_with_results + "/Ensemble_results")

    # Ask the user if they want to run the default ensemble method.
    answer = ""
    while answer not in ["Y", "N"]:
        answer = utils.input_with_colours("Architect: Do you wish to run the default ensemble method (HIGHLY RECOMMENDED)? [y/n] ")
        answer = answer.strip().upper()
        if answer == "Q":
            status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
            status_writer.close()
            exit()

    method = ""
    parameters = ""
    if answer == "Y":
        status_writer.write("Step_4: " + str(datetime.datetime.now()) + ": User wishes to use the default method and parameters.\n")
    else:
        while method not in ["Majority", "EC_specific", "NB", "Regression", "RF"]:
            method = utils.input_with_colours("Architect: Please specify the method to run ensemble approach with.\n" + \
                "Choose between: Majority, EC_specific, NB, Regression, RF. (case-sensitive):\n")
            if method.strip().upper() == "Q":
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                status_writer.close()
                exit()
            status_writer.write("Step_4: " + str(datetime.datetime.now()) + ": User wishes to use:\n Method_of_choice:  " + method + ".\n")
        parameters = utils.input_with_colours("Architect: Please specify the parameters to run ensemble approach with.\n" + \
            "Leave blank to use default for " + method + "\n")
        if parameters.strip().upper() == "Q":
            status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
            status_writer.close()
            exit()
        status_writer.write("Step_4: " + str(datetime.datetime.now()) + ": User wishes to use the following parameters:\n Parameters: " + parameters + "\n")

    
    # Now, use the option obtained from above and run the ensemble approach chosen.
    while True:
        method_command = ["python", architect_path + "/scripts/ensemble_enzyme_annotation/1_run_ensemble_approach.py"]
        method_command.append("-i")
        method_command.append(main_folder_with_results + "/Readable_results/readable_results.out")
        method_command.append("-t")
        method_command.append(utils.get_shell_to_python_readable_location(parameter_values["DATABASE"]) + "/enzyme_annotation")
        method_command.append("-o")
        method_command.append(main_folder_with_results + "/Ensemble_results")
        if method != "":
            method_command.append("-m")
            method_command.append(method)
        if parameters != "":
            method_command.append("-a")
            method_command.append(parameters)

        if parameters.strip().upper == "Q":
            status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
            status_writer.close()
            exit()

        # Try to run, and if there is an error, ask the user to check their entry again.
        try:
            subprocess.check_output(method_command, stderr=subprocess.STDOUT)
            break
        except Exception as e:
            status_writer.write("Step_4: " + str(datetime.datetime.now()) + ": Architect has found user's parameters to be incorrect.\n")
            parameters = utils.input_with_colours("Architect: Please specify the _correct_ parameters to run ensemble approach with.\n" + \
                "Leave blank to use default for " + method + "\n")
            status_writer.write("Step_4: " + str(datetime.datetime.now()) + ": User wishes to use the following parameters\n: Parameters: " + parameters + "\n")

    # Also find, if applicable, high-confidence predictions by at least 3 methods.
    status_writer.write("Step_4: " + str(datetime.datetime.now()) + ": If applicable, Architect will list predictions of EC that" + \
        " it has not been trained to predict.\n")
    additional_method_command = ["python", architect_path + "/scripts/ensemble_enzyme_annotation/x_list_ecs_left_out_by_trained_classifier.py"]
    additional_method_command.append("-i")
    additional_method_command.append(main_folder_with_results + "/Readable_results/readable_results.out")
    additional_method_command.append("-t")
    additional_method_command.append(utils.get_shell_to_python_readable_location(parameter_values["DATABASE"]))
    additional_method_command.append("-o")
    additional_method_command.append(main_folder_with_results + "/Ensemble_results")
    if method != "":
        additional_method_command.append("-m")
        additional_method_command.append(method)
    if parameters != "":
        additional_method_command.append("-a")
        additional_method_command.append(parameters)
    subprocess.call(additional_method_command)
    status_writer.write("Step_4: " + str(datetime.datetime.now()) + ": Architect finished running the chosen method.\n")
    status_writer.close()
    utils.print_with_colours("Architect: Enzyme annotation by ensemble approach done! Find your results under: " + main_folder_with_results + "/Ensemble_results")