from argparse import ArgumentParser
import utils

EQUATION = 'reaction.equation'
BOUNDS = 'reaction.bounds'
HIGH_CUTOFF = 0.5
LOW_CUTOFF = 0.0001

def read_column_from_file(file_name, column_n=1, delim="\t"):
    """Read elements in the nth column of this file.  Default is first column."""

    liste = set()
    with open(file_name) as input:
        for line in input:
            line = line.strip()
            if line == "":
                continue
            split = line.split(delim)
            curr_elem = split[column_n - 1]
            liste.add(curr_elem)
    return liste


def get_map_from_file(file_name, first_elem_is_key=True, need_values_in_set=True):

    key_value = {}
    with open(file_name) as input:
        for line in input:
            line = line.strip()
            if line == "":
                continue
            split = line.split("\t")
            if first_elem_is_key:
                key, value = split[0], split[1]
            else:
                key, value = split[1], split[0]
            utils.add_to_dict(key_value, key, value, need_values_in_set)
    return key_value


def write_out_subset_reactions(ecs_of_interest, ec_to_reactions, reaction_to_info, output_file, reactions_to_exclude=set()):
    """Write out the information available using only information from reaction_to_info. So, if there is information
    that is not available in reaction_to_info."""

    rxns_added = set()

    with open(output_file, "w") as writer:

        # Write out the reactions associated with ECs of interest.
        for ec in ecs_of_interest:
            if ec not in ec_to_reactions:
                continue
            curr_reactions = ec_to_reactions[ec]

            for rxn in curr_reactions:

                if rxn in reactions_to_exclude:
                    continue

                # If the reaction is also entered in the list of reactions already added, don't write it again
                # (would be redundant).
                if rxn in rxns_added:
                    continue

                rxns_added.add(rxn)

                # Write the information in the order specified by index_to_header.
                if rxn not in reaction_to_info:
                    continue
                acc_str = get_rxn_info_by_order(reaction_to_info[rxn])
                writer.write(rxn + ":\t" + acc_str + "\n")
    return rxns_added


def get_rxn_info_by_order(info, headers_in_order=[EQUATION, BOUNDS]):

    info_in_order = []
    for header in headers_in_order:
        info_in_order.append(info[header])
    acc_str = "\t".join(info_in_order)
    return acc_str


def read_and_split_conf_preds(ec_preds_file, high_cutoff, low_cutoff):

    high_conf_ecs = set()
    high_and_low_conf_ecs = set()
    with open(ec_preds_file) as input:
        for line in input:
            line = line.strip()
            if line == "":
                continue
            split = line.split("\t")
            
            if utils.is_num(split[-1]):
                ec, score = split[0], float(split[-1])
            else:
                ec, score = split[0], float(split[-2])
                
            if score > high_cutoff:
                high_conf_ecs.add(ec)
            if score > low_cutoff:
                high_and_low_conf_ecs.add(ec)

    return high_conf_ecs, high_and_low_conf_ecs


def get_reaction_name_to_modified_name(reaction_to_info):

    reaction_name_to_modified_name = {}
    modified_name_to_reaction_name = {}
    for modified_name in reaction_to_info:
        actual_reaction_name = modified_name.split("_")[0]
        reaction_name_to_modified_name[actual_reaction_name] = modified_name
        modified_name_to_reaction_name[modified_name] = actual_reaction_name
    return reaction_name_to_modified_name, modified_name_to_reaction_name


def get_info_for_one_reaction(elems, index_to_header={1:EQUATION, 2:BOUNDS}, indices_to_ignore=[0]):

    info = {}
    for index, elem in enumerate(elems):
        if index in indices_to_ignore:
            continue
        header = index_to_header[index]
        info[header] = elem
    return info


def get_reaction_to_equation_info(file_name, warning_reactions_to_exclude):

    reaction_to_equation_info = {}
    warning_reactions_info = {}
    with open(file_name) as input:
        for line in input:

            line = line.strip()
            if line == "":
                continue

            split = line.split("\t")
            reaction_abbrev = split[0].strip()[:-1]
            info = get_info_for_one_reaction(split)
            if reaction_abbrev not in warning_reactions_to_exclude:
                reaction_to_equation_info[reaction_abbrev] = info
            else:
                warning_reactions_info[reaction_abbrev] = info

    return reaction_to_equation_info, warning_reactions_info


def get_conf_to_tool(list_of_confs):

    conf_to_tool, tool_to_conf = {}, {}
    for tool, conf_level in zip(["CatFam", "DETECT", "EFICAz", "EnzDP", "PRIAM"], list_of_confs):
        tool_to_conf[tool] = conf_level
        utils.add_to_dict(conf_to_tool, conf_level, tool)
    return conf_to_tool, tool_to_conf


def supplement_from_additional_preds(additional_preds_file, min_num_high_conf, high_confidence_ecs, high_and_low_confidence_ecs):

    ecs_supplemented = set()
    start_parsing = False
    with open(additional_preds_file) as reader:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            if not start_parsing:
                if line.startswith("Protein_name"):
                    start_parsing = True
                continue

            split = line.split("\t")
            protein, ec = "\t".join(split[0:-6]), split[-6]
            conf_to_tool, tool_to_conf = get_conf_to_tool(split[2:])
            if ("2" not in conf_to_tool) or (len(conf_to_tool["2"]) < min_num_high_conf):
                continue
            if ec not in high_confidence_ecs:
                ecs_supplemented.add(ec)
                high_confidence_ecs.add(ec)
                high_and_low_confidence_ecs.add(ec)
    return high_confidence_ecs, high_and_low_confidence_ecs, ecs_supplemented


def write_out_ec_mapping(high_confidence_rxns, ec_to_reactions, high_confidence_ecs, ecs_supplemented, output_file):

    with open(output_file, "w") as writer:
        for ec in high_confidence_ecs:
            if ec not in ec_to_reactions:
                continue
            reactions = ec_to_reactions[ec]
            for reaction in reactions:
                if reaction not in high_confidence_rxns:
                    continue

                if ec not in ecs_supplemented:
                    writer.write(ec + "\t" + reaction + "\n")
                else:
                    writer.write(ec + "\t" + reaction + "\tEC likely to be present based solely on individual tools'"
                                                        "high-confidence predictions\n")


if __name__ == '__main__':

    parser = ArgumentParser(description="Contains functions for getting core reaction model and potential gap-filling"
                                        "reactions to add in.")
    parser.add_argument("--ec_preds_file", type=str, help="File containing predictions from pipeline.")
    parser.add_argument("--additional_preds_file", type=str, help="File containing additional predictions (from tools and not ensemble classifier)")
    parser.add_argument("--user_defined_file", type=str, help="File containing additional reactions that the user defines should be added, including biomass reaction.")
    parser.add_argument("--min_num_high_conf", type=int, default=3, help="Minimum number of tools predicting EC in additional_preds_file for consideration in high-confidence network")
    parser.add_argument("--database", type=str, help="Folder containing various information.")
    parser.add_argument("--output_folder", type=str, help="Folder to contain the output from this script (ie, high-confidence reactions)")

    args = parser.parse_args()
    ec_preds_file = args.ec_preds_file
    additional_preds_file = args.additional_preds_file
    user_defined_file = args.user_defined_file
    min_num_high_conf = args.min_num_high_conf
    database = args.database
    output_folder = args.output_folder

    high_confidence_ecs, high_and_low_confidence_ecs = read_and_split_conf_preds(ec_preds_file, HIGH_CUTOFF, LOW_CUTOFF)
    high_confidence_ecs, high_and_low_confidence_ecs, ecs_supplemented = \
        supplement_from_additional_preds(additional_preds_file, min_num_high_conf, high_confidence_ecs, high_and_low_confidence_ecs)
    ec_to_reactions = get_map_from_file(database + "/reaction_to_ec_no_spont_non_enz_reax.out", False)
    reactions_with_warnings = read_column_from_file(database + "/WARNING_reactions_with_formulaless_cpds.out");
    reaction_to_info, warning_rxn_to_info = \
        get_reaction_to_equation_info(database + "/SIMULATION_universe_rxn.out", reactions_with_warnings)

    # reaction_name_to_modified_name, modified_name_to_reaction_name = get_reaction_name_to_modified_name(reaction_to_info)
    # warning_reaction_name_to_modified_name, _ = get_reaction_name_to_modified_name(warning_rxn_to_info)

    # Write the high-confidence reactions and append default reactions and spontaneous reactions.
    high_confidence_rxns = write_out_subset_reactions(high_confidence_ecs, ec_to_reactions, reaction_to_info, \
        output_folder + "/SIMULATION_high_confidence_reactions.out")
    write_out_ec_mapping(high_confidence_rxns, ec_to_reactions, high_confidence_ecs, ecs_supplemented, \
        output_folder + "/MAP_high_confidence_reactions.out")
    utils.append_default_reactions(output_folder + "/SIMULATION_high_confidence_reactions.out",
                             database + "/SIMULATION_default_additional_reactions.out")
    utils.append_default_reactions(output_folder + "/SIMULATION_high_confidence_reactions.out",
                             database + "/SIMULATION_spontaneous_or_non_enzymatic.out")
    utils.append_default_reactions(output_folder + "/SIMULATION_high_confidence_reactions.out",
                             user_defined_file, True)

    # Write out the high-conf reactions for which we have a warning.
    extra_high_warning_rxns = write_out_subset_reactions(high_confidence_ecs, ec_to_reactions, warning_rxn_to_info,
                                                    output_folder + "/EXTRA_high_conf_reactions_for_further_considerations.out")

    # Also, write out all the confidence reactions and append the default reactions.
    high_and_low_confidence_rxns = write_out_subset_reactions(high_and_low_confidence_ecs, ec_to_reactions, reaction_to_info,
                                                               output_folder + "/SIMULATION_low_and_high_confidence_reactions.out")

    low_confidence_rxns_only = high_and_low_confidence_rxns - high_confidence_rxns
    low_confidence_ecs = high_and_low_confidence_ecs - high_confidence_ecs
    write_out_ec_mapping(low_confidence_rxns_only, ec_to_reactions, low_confidence_ecs, [],
                         output_folder + "/MAP_low_confidence_reactions.out")

    # Write out the low-confidence reactions for which we have warnings.  Append the default reactions and the spontaneous reactions as well.
    extra_low_warning_rxns = write_out_subset_reactions(low_confidence_ecs, ec_to_reactions, warning_rxn_to_info,
                                                    output_folder + "/EXTRA_low_conf_reactions_for_further_considerations.out",
                                                        extra_high_warning_rxns)

    utils.append_default_reactions(output_folder + "/SIMULATION_low_and_high_confidence_reactions.out",
                             database + "/SIMULATION_default_additional_reactions.out")
    utils.append_default_reactions(output_folder + "/SIMULATION_low_and_high_confidence_reactions.out",
                             database + "/SIMULATION_spontaneous_or_non_enzymatic.out")
    utils.append_default_reactions(output_folder + "/SIMULATION_low_and_high_confidence_reactions.out",
                             user_defined_file, True)