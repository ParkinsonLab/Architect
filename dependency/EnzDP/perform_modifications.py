from argparse import ArgumentParser

def add_modification_info(filename_to_num_to_new_line, curr_file_name, line_num, new_line):

    if curr_file_name not in filename_to_num_to_new_line:
        filename_to_num_to_new_line[curr_file_name] = {}
    filename_to_num_to_new_line[curr_file_name][line_num] = new_line


def read_modifications(modifications_file):

    filename_to_num_to_new_line = {}
    with open(modifications_file) as reader:
        for curr_line in reader:
            if curr_line.strip() == "":
                continue
            if curr_line[0] == "#":
                curr_file_name = curr_line[1:].strip()
            else:
                line_num = int(curr_line.split(":")[0])
                new_line = ":".join(curr_line.split(":")[1:])
                new_line = new_line.rstrip()
                add_modification_info(filename_to_num_to_new_line, curr_file_name, line_num, new_line)
    return filename_to_num_to_new_line


def read_num_to_line_of_file(file_name):

    num_to_line = {}
    with open(file_name) as reader:
        for i, line in enumerate(reader):
            num_to_line[i] = line
    return num_to_line


def modify_current_file(complete_path_to_file, num_to_original_line, num_to_new_line):

    last_line = max(max(num_to_original_line.keys()), max(num_to_new_line.keys()))
    with open(complete_path_to_file, "w") as writer:
        num = 0
        while num <= last_line:
            if num in num_to_new_line:
                writer.write(num_to_new_line[num] + "\n")
            else:
                writer.write(num_to_original_line[num])
            num += 1


if __name__ == '__main__':

    parser = ArgumentParser(description="Performs modifications to original EnzDP code for use by Architect.")
    parser.add_argument("--enzdp_path", type=str, help="Path where EnzDP original code is downloaded", required=True)
    parser.add_argument("--architect_path", type=str, help="Path where Architect was downloaded", required=True)

    args = parser.parse_args()
    enzdp_path = args.enzdp_path
    architect_path = args.architect_path

    filename_to_num_to_new_line = read_modifications(architect_path + "/dependency/EnzDP/summary_of_modifications.out")
    for file_to_modify, num_to_new_line in filename_to_num_to_new_line.iteritems():
        path_to_file_to_modify = enzdp_path + "/" + file_to_modify
        num_to_original_line = read_num_to_line_of_file(path_to_file_to_modify)
        modify_current_file(path_to_file_to_modify, num_to_original_line, num_to_new_line)