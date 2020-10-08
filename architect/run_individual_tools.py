import os
import sys
from argparse import ArgumentParser
import datetime
import subprocess
import utils


def get_tools_to_run_from_status_file(status_file):
    
    tools_to_run = []
    open_file = open(status_file)
    for line in open_file:
        if line.strip() == "":
            continue
        if line.startswith("\tTool_of_interest:"):
            tool = line.strip().split(":")[1]
            tools_to_run.append(tool)
        if utils.TERMINATION in line:
            open_file.close()
            exit()
        if utils.ALREADY_RAN_ENZ_TOOL in line:
            open_file.close()
            exit()
    open_file.close()
    return tools_to_run


def set_up_submit_script(submit_file_script, tools_to_run):

    if len(tools_to_run) == 0:
        return False

    with open(submit_file_script, "w") as writer:

        writer.write("BASEDIR=$(dirname \"$0\")\n")

        if "CatFam" in tools_to_run:
            writer.write("cd $BASEDIR\n")
            writer.write("cd CatFam\nsbatch run_catfam.sh\n")
            writer.write("\n")
        if "DETECT" in tools_to_run:
            writer.write("cd $BASEDIR\n")
            writer.write("cd DETECT\nsbatch run_detect.sh\n")
            writer.write("\n")
        if "EFICAz" in tools_to_run:
            writer.write("cd $BASEDIR\n")
            writer.write("cd EFICAz\n")
            writer.write("sh individualize.sh\n")
            writer.write("cd Scripts\n")
            writer.write("for script in `ls`; do\n\tsbatch $script\ndone\n")
            writer.write("\n")
        if "EnzDP" in tools_to_run:
            writer.write("cd $BASEDIR\n")
            writer.write("cd EnzDP\nsh individualize_project.sh\nsbatch run_enzdp.sh\n")
            writer.write("\n")
        if "PRIAM" in tools_to_run:
            writer.write("cd $BASEDIR\n")
            writer.write("cd PRIAM\nsbatch run_priam.sh")
            writer.write("\n")
    return True


if __name__ == '__main__':

    current_working_directory = os.getcwd()
    sys.path.append(current_working_directory)

    parser = ArgumentParser(description="Runs the scripts for the individual enzyme annotation tools.")
    parser.add_argument("--project_name", type=str, help="Name of the project (eg: organism name).", required=True)
    parser.add_argument("--output_dir", type=str, help="Location of project directory (default: current working directory).", required=False, default=current_working_directory)

    args = parser.parse_args()
    output_dir = args.output_dir
    project_name = args.project_name

    status_file = output_dir + "/" + args.project_name + "/architect_status.out"
    tools_to_run = get_tools_to_run_from_status_file(status_file)
    # print(tools_to_run)

    submit_file_script = output_dir + "/" + args.project_name + "/submit_tools.sh"
    at_least_one = set_up_submit_script(submit_file_script, tools_to_run)

    status_writer = open(status_file, "a")
    status_writer.write("Step_2:" + str(datetime.datetime.now()) + ": " + utils.ABOUT_TO_RUN_ENZ_TOOL + "\n")
    if at_least_one:
        subprocess.call(['sh', submit_file_script]) 
        status_writer.write("Step_2:" + str(datetime.datetime.now()) + ": Architect has started running the individual tools.\n")
    else:
        status_writer.write("Step_2:" + str(datetime.datetime.now()) + ": Architect was not given any tools to run.\n")
    status_writer.close()