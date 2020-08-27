from argparse import ArgumentParser
import glob
import os

def is_folder(pathname):

    return os.path.isdir(pathname)


def add_to_file(input_file, writer, tool):

    open_file = open(input_file)
    for line in open_file:
        line = line.strip()
        if line == "":
            continue
        # DETECT
        if line == "ID\tEC\tprobability\tpositive_hits\tnegative_hits":
            continue
        # EnzDP
        if (line[0] == ">") and (tool == "EnzDP"):
            continue
        writer.write(line + "\n")
    open_file.close()


def concatenate_results(result_string_output, output_file, tool):

    result_files = []
    if is_folder(result_string_output):
        if tool == "EnzDP":
            result_files = glob.glob(result_string_output + "/*.out")
        elif tool == "EFICAz":
            result_files = glob.glob(result_string_output + "/*/*.ecpred")
        else:
            result_files = glob.glob(result_string_output + "/*")
    else:
        result_files.append(result_string_output)
    writer = open(output_file, 'w')
    for result_file in result_files:
        add_to_file(result_file, writer, tool)
    writer.close()


if __name__ == '__main__':

    parser = ArgumentParser(description="Concatenates the results from each of the tools.")
    parser.add_argument("--output_folder", type=str, help="Folder where the raw results will be written.",
                        required=True)
    parser.add_argument("--catfam_results", type=str, help="Path to the results from CatFam.")
    parser.add_argument("--detect_results", type=str, help="Path to the results from DETECT.")
    parser.add_argument("--eficaz_results", type=str, help="Path to the results from EFICAz.")
    parser.add_argument("--enzdp_results", type=str, help="Path to the results from EnzDP.")
    parser.add_argument("--priam_results", type=str, help="Path to the results from PRIAM.")

    args = parser.parse_args()
    output_folder = args.output_folder
    catfam_results = args.catfam_results
    detect_results = args.detect_results
    eficaz_results = args.eficaz_results
    enzdp_results = args.enzdp_results
    priam_results = args.priam_results

    for tool, results in \
            zip(["CatFam", "DETECT", "EFICAz", "EnzDP", "PRIAM"], \
                [catfam_results, detect_results, eficaz_results, enzdp_results, priam_results]):
        concatenate_results(results, output_folder + "/" + tool + "/CONCATENATED_" + tool + ".out", tool)