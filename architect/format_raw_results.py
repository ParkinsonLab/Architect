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
    parser.add_argument("--project_name", type=str, help="Name of the project (eg: organism name).", required=True)
    parser.add_argument("--output_dir", type=str, help="Location of project directory (default: current working directory).", required=False, default=current_working_directory)
    parser.add_argument("--arguments_file", type=str, help="File with the values of the parameters.", required=True)

    args = parser.parse_args()
    output_dir = args.output_dir
    project_name = args.project_name
    arguments_file = args.arguments_file

    parameter_values = utils.read_parameter_values(arguments_file)
    parameter_values["SEQUENCE_FILE"] = utils.get_shell_to_python_readable_location(parameter_values["SEQUENCE_FILE"])

    status_file = output_dir + "/" + project_name + "/architect_status.out"
    main_folder_with_results = output_dir +  "/" + project_name + "/Ensemble_annotation_files"
    if not os.path.isdir(main_folder_with_results):
        os.mkdir(main_folder_with_results)

    # First verify that the user has not quit.
    if utils.user_has_quit(status_file) or utils.just_ran_tools(status_file):
        exit()

    status_writer = open(status_file, "a")

    # Ask the user if they want to provide the location of the results, or proceed with the default location of results.
    answer = ""
    while answer not in ["Y", "N"]:
        answer = input("Architect: Do you wish to proceed with the default location of results? [y/n] ")
        answer = answer.strip().upper()
        if answer == "Q":
            status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
            status_writer.close()
            exit()

    tool_to_location = {"CatFam": None, "DETECT": None, "EFICAz": None, "EnzDP": None, "PRIAM": None}

    if answer == "N":
        print ("Architect: Please provide the absolute location of the concatenated results for each of the following tools.\n" + \
            "Architect: Leave blank if not available (not recommended).\n")
        for tool in sorted(tool_to_location.keys()):
            answer = input(tool + ": ")
            answer = answer.strip()
            if answer.upper() == "Q":
                status_writer.write("Termination:" + str(datetime.datetime.now()) + ": " + utils.TERMINATION + "\n")
                status_writer.close()
                exit()
            if answer != "":
                # Verify that file exists.
                while not (os.path.isfile(utils.get_shell_to_python_readable_location(answer.strip()) ) ):
                    answer = input("Architect: No file found. Please enter absolute location again or leave blank to exclude tool.\n" + tool + ": ")
                    if answer == "":
                        continue
                tool_to_location[tool] = utils.get_shell_to_python_readable_location(answer.strip())
                status_writer.write("Step_3: " + str(datetime.datetime.now()) + ": User has specified " + tool + "'s results in " + answer + ".\n")
    else:
        # Get the default location of the results and populate tool_to_location.
        prepend_folder_name = output_dir + "/" + project_name
        catfam_folder = prepend_folder_name + "/CatFam/Results"
        detect_file = prepend_folder_name + "/DETECT/output_40.out"
        eficaz_folder = prepend_folder_name + "/EFICAz/Results"
        enzdp_folder = prepend_folder_name + "/EnzDP/Results"
        priam_file = prepend_folder_name + "/PRIAM/PRIAM_Results/PRIAM_test/ANNOTATION/sequenceECs.txt"

        # Unzip EFICAz results.
        unzip_script = prepend_folder_name + "/EFICAz/unzip_results.sh"
        with open(unzip_script, "w") as unzip_writer:
            unzip_writer.write("cd " + eficaz_folder + "\n")
            unzip_writer.write("for file in `ls`; do\n\ttar -xzvf $file;\ndone\n")
        subprocess.call(['sh', unzip_script])

        # Concatenate the raw results.
        raw_results_command = ["python", "scripts/ensemble_enzyme_annotation/0_concatenate_raw_results.py"]
        raw_results_command.append("--output_folder")
        raw_results_command.append(prepend_folder_name)
        for flag, location in zip(["--catfam_results", "--detect_results", "--eficaz_results", "--enzdp_results", "--priam_results"], \
            [catfam_folder, detect_file, eficaz_folder, enzdp_folder, priam_file]):
            raw_results_command.append(flag)
            raw_results_command.append(location)
        subprocess.call(raw_results_command)

        status_writer.write("Step_3: " + str(datetime.datetime.now()) + ": Results from individual tools have been concatenated.\n")

        for tool in ["CatFam", "DETECT", "EFICAz", "EnzDP", "PRIAM"]:
            tool_to_location[tool] = prepend_folder_name + "/" + tool + "/CONCATENATED_" + tool + ".out"

    # Now, format the raw results (0_format_raw_results.py, 0_get_readable_results.py).
    format_raw_command = ["python", "scripts/ensemble_enzyme_annotation/0_format_raw_results.py"]
    format_raw_command.append("--output_folder")
    format_raw_command.append(main_folder_with_results + "/Formatted_results")
    format_raw_command.append("--fasta_file")
    format_raw_command.append(parameter_values["SEQUENCE_FILE"])
    for tool, location in tool_to_location.items():
        if location is None:
            continue
        format_raw_command.append("--" + tool.lower() + "_raw")
        format_raw_command.append(location)
    os.mkdir(main_folder_with_results + "/Formatted_results")
    subprocess.call(format_raw_command)
    status_writer.write("Step_3: " + str(datetime.datetime.now()) + ": Results from individual tools have been made into the same format.\n")

    get_readable_command = ["python", "scripts/ensemble_enzyme_annotation/0_get_readable_results.py"]
    get_readable_command.append("-i")
    get_readable_command.append(main_folder_with_results + "/Formatted_results")
    get_readable_command.append("-o")
    get_readable_command.append(main_folder_with_results + "/Readable_results/readable_results.out")
    os.mkdir(main_folder_with_results + "/Readable_results")
    subprocess.call(get_readable_command)
    status_writer.write("Step_3: " + str(datetime.datetime.now()) + ": Results from individual tools have been written altogether into the same file.")

    status_writer.close()