from argparse import ArgumentParser
import utils

KEY_EQUATION = 'reaction.equation'
KEY_LB = 'reaction.lb'
KEY_UB = 'reaction.ub'

DEFAULT_LB = -1000
DEFAULT_UB = 1000

DEADEND_HIGH_CONF = "DEADEND_HIGH_"
DEADEND_LOW_CONF_ONLY = "DEADEND_LOW_ONLY_"


def get_deadend_metabolites(rxn_to_info, metabolite_to_rxn):

    deadend_metabolites = set()
    reversible_reactions_found = set()
    reactions_seen = set()

    maybe_deadend = True

    for metabolite, rxns in metabolite_to_rxn.items():
        # If metabolite is involved in a single reaction, then DEADEND.
        maybe_deadend = True
        if len(rxns) == 1:
            deadend_metabolites.add(metabolite)
        else:
            # If one of the reactions is reversible, the metabolite is not DEADEND.
            # Otherwise, if there are no reactions either consuming or producing the metabolite, then the metabolite is
            # DEADEND.
            substrate_rxns = []
            product_rxns = []
            for rxn in rxns:
                if rxn in reversible_reactions_found:
                    maybe_deadend = False
                    break
                elif rxn not in reactions_seen:
                    if is_reversible(rxn, rxn_to_info):
                        reversible_reactions_found.add(rxn)
                        reactions_seen.add(rxn)
                        maybe_deadend = False
                        break
                # If you get here, the reaction is not reversible.
                substrate_side = rxn_to_info[rxn][KEY_EQUATION].split(">")[0]
                if substrate_side.find(metabolite) != -1:
                    substrate_rxns.append(rxn)
                else:
                    product_rxns.append(rxn)

            # If of the reactions you have found, you only have reactions either consuming or producing the metabolite,
            # this metabolite is a deadend.
            if maybe_deadend:
                if len(substrate_rxns) == 0 or len(product_rxns) == 0:
                    deadend_metabolites.add(metabolite)
                maybe_deadend = True
    return deadend_metabolites


def is_reversible(rxn, rxn_to_info):

    return ((rxn_to_info[rxn][KEY_LB] < 0) and (rxn_to_info[rxn][KEY_UB] > 0))


def get_difference(set_1, set_2):
    '''Return set_1 - set_2.'''

    return set_1 - set_2


def get_sum(set_1, set_2):
    '''Return set_1 + set_2.'''

    return set(list(set_1) + list(set_2))


def get_exchange_reactions(high_conf_deadend_mets, low_and_high_conf_deadend_mets,
                           deadend_high_conf=DEADEND_HIGH_CONF, deadend_low_conf_only=DEADEND_LOW_CONF_ONLY,
                           lb=DEFAULT_LB, ub=DEFAULT_UB):
    '''Returns {reaction_name: [equation: value, lb: value, ub: value]}'''

    new_reactions_to_info = {}
    i = 0
    # High-confidence deadend metabolites.
    for metabolite in high_conf_deadend_mets:
        reaction_name = deadend_high_conf + str(i)
        equation = metabolite + ' <->'
        new_reactions_to_info[reaction_name] = {KEY_EQUATION: equation, KEY_LB: lb, KEY_UB: ub}
        i += 1

    i = 0
    # Get those deadend metabolites
    for metabolite in low_and_high_conf_deadend_mets:
        if metabolite in high_conf_deadend_mets:
            continue
        reaction_name = deadend_low_conf_only + str(i)
        equation = metabolite + ' <->'
        new_reactions_to_info[reaction_name] = {KEY_EQUATION: equation, KEY_LB: lb, KEY_UB: ub}
        i += 1
    return new_reactions_to_info


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


if __name__ == '__main__':

    parser = ArgumentParser(description="Contains functions for getting core reaction model and potential gap-filling"
                                        "reactions to add in.")
    parser.add_argument("--database", type=str, help="Folder containing various information.")
    parser.add_argument("--output_folder", type=str, help="Folder to contain the output from this script (ie, a set "
                                                          "of reactions that can be picked for gap-filling)")

    args = parser.parse_args()
    database = args.database
    output_folder = args.output_folder

    input_high_conf_model_file = output_folder + "/SIMULATION_high_confidence_reactions.out"
    input_low_and_high_conf_model_file = output_folder + "/SIMULATION_low_and_high_confidence_reactions.out"
    input_universe_without_exchange_reactions = database + "/SIMULATION_universe_rxn.out"
    output_candidates_with_exchange_reactions = output_folder + "/SIMULATION_augmented_gapfill_candidates.out"
    output_only_candidates = output_folder + "/SIMULATION_only_gapfill_candidates.out"
    file_with_content_to_ignore = database + "/SIMULATION_metabolites_with_default_exchanges.out"
    problematic_reactions_with_missing_info = database + "/WARNING_reactions_with_formulaless_cpds.out"

    # Load the various model info.
    # (1) For the candidate reactions to gapfill, exclude those reactions that are already found in the high-confidence set of reactions.
    #     Also, exclude any warning reactions from consideration, when reading from the universe set.
    high_conf_model_rxn_to_info, high_conf_model_met_to_rxn = utils.read_model_file(input_high_conf_model_file)
    low_and_high_conf_model_rxn_to_info, low_and_high_conf_model_met_to_rxn = utils.read_model_file(input_low_and_high_conf_model_file)
    warning_rxns = read_column_from_file(problematic_reactions_with_missing_info)
    candidate_rxn_to_info, candidate_met_to_rxn = utils.read_model_file(input_universe_without_exchange_reactions,
                                                                  warning_rxns.union(set(high_conf_model_rxn_to_info.keys())) )

    # (2) First, get the deadend metabolites from the high-confidence network.
    metabolites_to_ignore = read_column_from_file(file_with_content_to_ignore)
    high_conf_deadend_metabolites = get_deadend_metabolites(high_conf_model_rxn_to_info, high_conf_model_met_to_rxn)
    high_conf_deadend_metabolites = get_difference(high_conf_deadend_metabolites, metabolites_to_ignore)
    exchange_reactions = get_exchange_reactions(high_conf_deadend_metabolites, [])

    # (3) In the universal model, include the low-confidence reactions and the exchange reactions I have mentioned above.
    #   an additional file with the high-confidence reactions as well.
    utils.write_model_with_new_reactions(candidate_rxn_to_info, exchange_reactions, output_only_candidates)
    utils.write_model_with_new_reactions(candidate_rxn_to_info, exchange_reactions,
                                   output_candidates_with_exchange_reactions)
    utils.append_default_reactions(output_candidates_with_exchange_reactions, input_high_conf_model_file)