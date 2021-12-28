import architect.utils
import shutil
import os
import subprocess
from argparse import ArgumentParser

def verify_if_tool_to_be_downloaded(tool_name, path_for_tools, create_dir=True):
    """Verifies if the tool needs to be downloaded.  Returns True if and only it is the case.
    If tools is to be downloaded, create directory with the same name if create_dir"""

    architect.utils.print_with_colours("Architect_tools_set_up: " + tool_name + " installation.")

    # Check if the directory exists. If it does, tell the user you've seen this folder.  Do they want to download it?
    if os.path.exists(path_for_tools + "/" + tool_name):
        response = ""
        while response not in ["Y", "N"]:
            architect.utils.print_warning("Architect_tools_set_up: Folder " + tool_name + " exists.  Keep installing?  Folder contents will be overwritten. (y/n)")
            response = raw_input()
            response = response.strip().upper()
        status = (response == "Y")

    # If the directory is not present, ask if they want to download it.
    else:
        response = ""
        while response not in ["Y", "N"]:
            architect.utils.print_warning("Architect_tools_set_up: Do you wish to install " + tool_name + " (recommended)? (y/n)")
            response = raw_input()
            response = response.strip().upper()
        status = (response == "Y")

    if status and create_dir and (not os.path.exists(path_for_tools + "/" + tool_name)):
        os.makedirs(path_for_tools + "/" + tool_name)

    return status


def download_to_directory(url_address, output_folder):

    subprocess.call(["wget", url_address, "-O", output_folder])


def clone_to_directory(url_address, output_folder):

    subprocess.call(["git", "clone", url_address, output_folder])

def untar_file(tarred_file, output_folder):

    subprocess.call(["tar", "-xzvf", tarred_file, "-C", output_folder])


def unzip_file(zipped_file, output_folder):

    subprocess.call(["unzip", zipped_file, "-d", output_folder])


def delete_file(file_name):

    os.remove(file_name)


def delete_folder_recursively(folder_name):

    shutil.rmtree(folder_name)


def move_files(original_path, new_path):

    shutil.move(original_path, new_path)


def set_up_eficaz(eficaz_folder):

    writer = open("set_up_eficaz.sh", "w")
    writer.write("cd " + eficaz_folder + "/bin\n")
    writer.write("./INSTALL")
    writer.close()
    subprocess.call(["sh", "set_up_eficaz.sh"])

    delete_file("set_up_eficaz.sh")


def set_up_priam(path_for_db, path_for_search_tool, blast_bin_location):
    """This sets up PRIAM by running PRIAM on an empty fasta file."""

    writer = open("empty.fa", "w")
    writer.close()

    lines = ["PRIAM_SEARCH=" + path_for_search_tool]
    lines.append("PRIAM_profiles_library=" + path_for_db)
    lines.append("TEST=empty.fa")
    lines.append("BLAST_BIN=" + blast_bin_location)
    lines.append("java -jar ${PRIAM_SEARCH} -n 'test' -i $TEST -p $PRIAM_profiles_library -o 'PRIAM_set_up' --bd $BLAST_BIN")

    priam_run_file = "set_up_priam.sh"
    writer = open(priam_run_file, "w")
    writer.write("\n".join(lines))
    writer.close()

    subprocess.call(["sh", "set_up_priam.sh"])
    delete_file("set_up_priam.sh")
    delete_folder_recursively("PRIAM_set_up")


if __name__ == '__main__':

    parser = ArgumentParser("Runs enzyme annotation tools used by Architect interactively.")
    parser.add_argument("--i", type=str, help="Specifies if running outside of Docker if and only if True.", \
        choices=["yes", "no"], default="No")

    args = parser.parse_args()
    outside_docker = (args.i == "yes")

    architect.utils.print_with_colours("\nWelcome to Architect's tool downloader!")
    architect.utils.print_with_colours("This utility--only meant to be run once--will install the enzyme annotation tools " + \
        "used by Architect.")
    user_proceed = ""
    while user_proceed not in ["Y", "N"]:
        user_proceed = architect.utils.input_with_colours("Do you need to download any tools? (y/n)")
        user_proceed = user_proceed.strip().upper()
    if user_proceed == "N":
        exit()

    architect.utils.print_warning("\nYou have now entered Architect's downloader.")

    # Step 1: Set up the folder where files are going to be downloaded. 
    # Default is under where Architect has been downloaded and in its dependency folder.
    # Otherwise, create a new folder where all this will be downloaded (if it doesn't exist yet).
    user_proceed = ""
    if outside_docker:
        path_for_tools = "indiv_tools"
        while user_proceed not in ["Y", "N"]:
            user_proceed = architect.utils.input_with_colours("Architect_tools_set_up: By default, download will be in this directory under 'indiv_tools'. Proceed with default? (y/n)")
            user_proceed = user_proceed.strip().upper()
        if user_proceed == "N":
            path_for_tools = architect.utils.input_with_colours("Architect_tools_set_up: Please enter the complete path where you wish the download to happen.")
    else:
        path_for_tools = "/indiv_tools"
        architect.utils.print_warning("Architect_tools_set_up: Tools will be downloaded in the specified directory under 'indiv_tools'.")
    if not os.path.exists(path_for_tools):
        os.makedirs(path_for_tools)

    architect.utils.print_warning("Architect_tools_set_up: You will be prompted for whether you wish to run each tool.")
    architect.utils.print_warning("Architect_tools_set_up: Please note that some tools may take longer to install than others")

    # Step 2: Download CatFam.
    download_tool = verify_if_tool_to_be_downloaded("CatFam", path_for_tools)
    if download_tool:
        catfam_url = "http://www.bhsai.org/downloads/catfam.tar.gz"
        path_of_tarred = path_for_tools + "/CatFam/catfam.tar.gz"
        download_to_directory(catfam_url, path_of_tarred)
        untar_file(path_of_tarred, path_for_tools + "/CatFam")
        delete_file(path_of_tarred)

    # Step 3: Download DETECT.
    download_tool = verify_if_tool_to_be_downloaded("DETECTv2", path_for_tools, False)
    if download_tool:
        detect_url = "http://compsysbio.org/projects/DETECTv2/DETECTv2.tar.gz"
        path_of_tarred = path_for_tools + "/DETECTv2.tar.gz"
        download_to_directory(detect_url, path_of_tarred)
        untar_file(path_of_tarred, path_for_tools)
        delete_file(path_of_tarred)

    # Step 4: Download EFICAz.
    download_tool = verify_if_tool_to_be_downloaded("EFICAz2.5.1", path_for_tools, False)
    if download_tool:
        eficaz_url = "http://cssb2.biology.gatech.edu/4176ef47-d63a-4dd8-81df-98226e28579e/EFICAz2.5.1.tar.gz"
        path_of_tarred = path_for_tools + "/EFICAz2.5.1.tar.gz"
        download_to_directory(eficaz_url, path_of_tarred)
        untar_file(path_of_tarred, path_for_tools)
        delete_file(path_of_tarred)
        set_up_eficaz(path_for_tools + "/EFICAz2.5.1")

    # Step 5: Download EnzDP.
    download_tool = verify_if_tool_to_be_downloaded("EnzDP", path_for_tools, False)
    if download_tool:
        enzdp_folder = path_for_tools + "/EnzDP"
        path_of_cloned = path_for_tools + "/tmp_EnzDP"
        os.makedirs(path_of_cloned)
        enzdp_url = "https://bitbucket.org/ninhnn/enzdp/src/master/"
        
        clone_to_directory(enzdp_url, path_of_cloned)
        delete_file(path_of_cloned + "/EnzDP_src.zip")
        move_files(path_of_cloned + "/trunk", enzdp_folder)
        delete_folder_recursively(path_of_cloned)
        unzip_file(enzdp_folder + "/HMMs.zip", enzdp_folder)
        delete_file(enzdp_folder + "/HMMs.zip")

        modify_enzdp = "dependency/EnzDP/perform_modifications.py"
        architect_directory = os.path.dirname(os.path.abspath(__file__))
        subprocess.call(["python", modify_enzdp, "--enzdp_path", enzdp_folder, "--architect_path", architect_directory])

    # Step 6: Download PRIAM.
    download_tool = verify_if_tool_to_be_downloaded("PRIAM", path_for_tools)
    if download_tool:
        priam_url = "http://priam.prabi.fr/REL_JAN18/Distribution.zip"
        search_tool_url = "http://priam.prabi.fr/utilities/PRIAM_search.jar"
        path_of_zipped = path_for_tools + "/PRIAM/Distribution.zip"
        path_of_search_tool = path_for_tools + "/PRIAM/PRIAM_search.jar"
        path_for_priam_db = path_for_tools + "/PRIAM/PRIAM_JAN18"
        
        path_for_blast_bin = "/tools/BLAST_legacy/bin"
        if outside_docker:
            path_for_blast_bin = architect.utils.input_with_colours("Please enter complete path to blast bin folder.  See Architect's README for more information.")

        download_to_directory(priam_url, path_of_zipped)
        unzip_file(path_of_zipped, path_for_tools + "/PRIAM")
        delete_file(path_of_zipped)
        
        download_to_directory(search_tool_url, path_of_search_tool)
        set_up_priam(path_for_priam_db, path_of_search_tool, path_for_blast_bin)

    architect.utils.print_with_colours("Architect_tools_set_up: Exiting the downloader.\n")