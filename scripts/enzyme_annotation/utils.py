import glob

def check_and_set_arguments(method, method_arguments, method_to_default, method_to_options):

    # If no values have been specified, set to default
    if not method_arguments:
        return method_to_default[method]
    else:
        method_arguments = check_options_are_complete(method_to_options[method], method_arguments)
        return method_arguments


def check_options_are_complete(list_of_list_of_options, specified_arguments):
    '''Has the user specified all options correctly?
    This is done by going through list_of_list_of_options which is structured as follows:
    [ [optionA1, optionA2, ... optionAm], [optionB1, optionB2, ... optionBn], ... ] where
    the user should specify exactly one element from each of the inner lists.'''

    new_specified_arguments = ""

    # If too few or more arguments than needed have been specified, then something is wrong with the user's
    # specifications.
    if len(list_of_list_of_options) != len(specified_arguments):
        raise ValueError("Wrong number of parameters specified")

    num_found = 0
    for list_of_options in list_of_list_of_options:
        for option in list_of_options:
            option = option.strip()
            if option in specified_arguments:
                new_specified_arguments = new_specified_arguments + "/" + option
                num_found += 1
                break

    # Have we found that exactly one element from each list from list_of_list_of_options has been specified?
    # If and only this is true, then, all options have been specified.
    if num_found == len(list_of_list_of_options):
        return new_specified_arguments[1:]
    else:
        raise ValueError("Wrong parameters specified")


def get_tool_to_cutoff(folder_name):
    '''In this folder, each file is a .cutoff file where the suffix represents the tool of interest.'''

    tool_to_cutoff = {}
    file_names = glob.glob(folder_name + "/*.cutoff")
    for file_name in file_names:
        if file_name.find("\\") != -1:
            tool = file_name.split("\\")[-1].split(".cutoff")[0]
        else:
            tool = file_name.split("/")[-1].split(".cutoff")[0]
        tool_to_cutoff[tool] = read_cutoffs(file_name)
    return tool_to_cutoff


def read_cutoffs(file_name):
    '''Read the cutoffs from this file.  If the same cutoff is to be applied for all ECs, read file formatted as
            ALL [TAB] cutoff
    and return cutoff.
    Otherwise, read file formatted as
            EC [TAB] cutoff
    and return a dictionary of EC to cutoff'''

    ec_to_cutoff = {}
    with open(file_name) as infile:
        for i, line in enumerate(infile):
            line = line.strip()
            if line == "":
                continue
            split = line.split()
            if i == 0 and split[0] == "ALL":
                return float(split[1])
            else:
                ec_to_cutoff[split[0]] = float(split[1])
    return ec_to_cutoff


def get_order_of_labels(method, method_arguments=""):

    if method == "NB":
        return ["CatFam", "DETECT", "EFICAz", "EnzDP", "PRIAM"]
    elif method == "Regression":
        return ["CatFam", "DETECT_low", "DETECT_high", "EFICAz_low", "EFICAz_high", "EnzDP_low", "EnzDP_high",
                       "PRIAM_low", "PRIAM_high"]
    elif method == "RF":
        return {"CatFam": [0, 2],
                       "DETECT_low": [1, 1],
                       "DETECT_high": [1, 2],
                       "EFICAz_low": [2, 1],
                       "EFICAz_high": [2, 2],
                       "EnzDP_low": [3, 1],
                       "EnzDP_high": [3, 2],
                       "PRIAM_low": [4, 1],
                       "PRIAM_high": [4, 2]}


def get_modified_tool_name(method, tool_to_cutoff_for_high_conf, tool, ec, score):

    if method in ["Majority", "NB"]:
        return [tool]
    if method == "EC_specific":
        if tool == "CatFam":
            return [tool]
        if is_high_conf(tool_to_cutoff_for_high_conf, tool, ec, score):
            return [tool + "_high_conf", tool]
        else:
            return [tool]
    if method in ["Regression", "RF"]:
        if tool == "CatFam":
            return [tool]
        if is_high_conf(tool_to_cutoff_for_high_conf, tool, ec, score):
            return [tool + "_high"]
        else:
            return [tool + "_low"]


def add_to_dict(key_value, key, value):

    if key not in key_value:
        s = set()
        s.add(value)
        key_value[key] = s
    else:
        key_value[key].add(value)


def is_high_conf(tool_to_cutoff_for_high_conf, tool, ec, score):

    if type(tool_to_cutoff_for_high_conf[tool]) is dict:
        cutoff = tool_to_cutoff_for_high_conf[tool][ec]
    else:
        cutoff = tool_to_cutoff_for_high_conf[tool]
    return score >= cutoff


def read_ec_to_predictable_tools(file_name):

    ec_to_predictable_tools = {}

    with open(file_name) as open_file:
        for i, line in enumerate(open_file):

            line = line.strip()
            if line == "":
                continue

            if i == 0:
                index_to_tool = {}
                split = line.split()
                for j, tool in enumerate(split):
                    index_to_tool[j] = tool
            else:
                split = line.split()
                ec = split[0]
                curr_set = set()
                bool_array = split[1:]
                for j, elem in enumerate(bool_array):
                    if elem == "FALSE":
                        continue
                    curr_set.add(index_to_tool[j])
                ec_to_predictable_tools[ec] = curr_set

    return ec_to_predictable_tools