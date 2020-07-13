from argparse import ArgumentParser
import glob

def get_seq_name(split):

    seq_name = split[0]
    i = 1
    while i < len(split) - 2:
        seq_name = seq_name + "\t" + split[i]
        i += 1
    return seq_name


def write_to_file(file_name, tool, writer):

    with open(file_name) as in_file:
        for line in in_file:
            line = line.strip()
            if line == "":
                continue
            split = line.split("\t")
            seq_name, ec, score = get_seq_name(split), split[-2], split[-1]
            new_line = seq_name + "\t" + tool + "\t" + ec + "\t" + score
            writer.write(new_line + "\n")
        in_file.close()


def get_tool_name_from_file_name(prefix, suffix, file_name):

    tools = ["CatFam", "DETECT", "EFICAz", "EnzDP", "PRIAM"]
    for tool in tools:
        if file_name.find(prefix + tool + suffix) != -1:
            return tool


if __name__ == '__main__':

    parser = ArgumentParser(description="Takes re-formatted predictions from each tool, and writes it in a format"
                                        "readable by the ensemble methods.")
    parser.add_argument("-i", "--input_folder", type=str,
                        help="Folder where all predictions from the different tools are.", required=True)
    parser.add_argument("-o", "--output_file", type=str, help="File where the readable predictions should be "
                                                              "written out to.", required=True)
    args = parser.parse_args()
    input_folder = args.input_folder
    output_file = args.output_file

    with open(output_file, "w") as writer:
        file_names = glob.glob(input_folder + "/*")
        for file_name in file_names:
            tool = get_tool_name_from_file_name("FORMATTED_", "_results.out", file_name)
            write_to_file(file_name, tool, writer)
