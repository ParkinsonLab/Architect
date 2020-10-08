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

    args = parser.parse_args()
    output_dir = args.output_dir
    project_name = args.project_name

    status_file = output_dir + "/" + args.project_name + "/architect_status.out"

    # First verify that the user has not quit.
    if utils.user_has_quit(status_file) or utils.just_ran_tools(status_file):
        exit()

    #TBC