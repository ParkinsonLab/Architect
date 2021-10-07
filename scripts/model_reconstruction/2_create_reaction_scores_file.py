from argparse import ArgumentParser
import utils

HIGH_CUTOFF = 0.5
LOW_CUTOFF = 0.0001

CUTOFF = 0.5

DEADEND_HIGH_CONF = "DEADEND_HIGH_import_"
DEADEND_LOW_CONF_ONLY = "DEADEND_LOW_ONLY_import_"


def add_to_score_dict(key_to_score, key, score):

    if key not in key_to_score:
        key_to_score[key] = score
    else:
        key_to_score[key] = max(key_to_score[key], score)


def read_ec_to_score(ec_preds_file):

    ec_to_score = {}
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
            
            add_to_score_dict(ec_to_score, ec, score)
    return ec_to_score


def get_low_conf(ec_to_score, high_cutoff=HIGH_CUTOFF, low_cutoff=LOW_CUTOFF):

    low_conf_ec_to_score = {}
    for ec, score in ec_to_score.items():
        if score <= high_cutoff and score > low_cutoff:
            low_conf_ec_to_score[ec] = score
    return low_conf_ec_to_score


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


def get_reaction_to_max_score(low_conf_ec_to_score, ec_to_reactions, gapfilling_candidates):

    reaction_to_score = {}
    for ec, score in low_conf_ec_to_score.items():
        # Get the KEGG reactions associated with this EC.
        if ec not in ec_to_reactions:
            continue
        kegg_reactions = ec_to_reactions[ec]

        for rxn in kegg_reactions:

            # Is this reaction not a gap-filling candidate?  If not, ignore!
            if rxn not in gapfilling_candidates:
                continue
            # I have to use this function in the case that this reaction was already entered in the model because it
            # is associated with another EC.
            add_to_score_dict(reaction_to_score, rxn, float(score))

    for reaction in gapfilling_candidates:
        if reaction in reaction_to_score:
            continue
        reaction_to_score[reaction] = 0.0

    return reaction_to_score


def write_out_reaction_to_score(reaction_to_score, reaction_to_normalized_score, penalty_exchange, reaction_score_file):

    deadend_score = 1/(1.0 * penalty_exchange) - 1

    with open(reaction_score_file, "w") as writer:
        writer.write("\t".join(["reaction", "normalized_score", "original_score"]) + "\n")
        for reaction in sorted(reaction_to_score.keys()):
            score = reaction_to_score[reaction]
            if (reaction.startswith(DEADEND_HIGH_CONF) or reaction.startswith(DEADEND_LOW_CONF_ONLY)):
                normalized_score = deadend_score
            else:
                normalized_score = reaction_to_normalized_score[reaction]
            writer.write("\t".join([reaction, str(normalized_score), str(score)]) + "\n")


def read_reactions_from_file(file_name):

    reactions = set()
    with open(file_name) as reader:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            reaction = line.split()[0][:-1]
            reactions.add(reaction)
    return reactions


def get_normalized_score(reaction_to_score):
    '''Return scores divided by median. (Ignoring zeroes)'''

    scores = []
    for _, score in reaction_to_score.items():
        if score < 0.00000001:
            continue
        scores.append(score)
    scores = sorted(scores)
    n = len(scores)
    
    index = int(n/2)
    # # If n is odd
    if (n == 0):
        median = 1.0
    elif (n % 2) == 1:
        median = scores[index] * 1.0
    # if n is even
    else:
        median = (scores[index] + scores[index - 1]) * 0.5

    reaction_to_normalized_score = {}
    for reaction, score in reaction_to_score.items():
        reaction_to_normalized_score[reaction] = score/median
    return reaction_to_normalized_score


if __name__ == '__main__':

    parser = ArgumentParser(description="Contains functions for getting core reaction model and potential gap-filling"
                                        "reactions to add in.")
    parser.add_argument("--ec_preds_file", type=str, help="File containing predictions from pipeline.")
    parser.add_argument("--penalty_exchange", type=float, help="Penalty for adding exchange reactions for deadend metabolites.", default=1.0)
    parser.add_argument("--database", type=str, help="Folder containing various information.")
    parser.add_argument("--output_folder", type=str,
                        help="Folder to contain the output from this script (ie, high-confidence reactions)")

    args = parser.parse_args()
    ec_preds_file = args.ec_preds_file
    penalty_exchange = args.penalty_exchange
    database = args.database
    output_folder = args.output_folder

    reaction_score_file = output_folder + "/SIMULATION_reaction_scores.out"

    ec_to_score = read_ec_to_score(ec_preds_file)
    low_conf_ec_to_score = get_low_conf(ec_to_score)

    ec_to_reactions = get_map_from_file(database + "/reaction_to_ec_no_spont_non_enz_reax.out", False)

    gapfill_candidates = read_reactions_from_file(output_folder + "/SIMULATION_augmented_gapfill_candidates.out")

    reaction_to_score = get_reaction_to_max_score(low_conf_ec_to_score, ec_to_reactions, gapfill_candidates)

    reaction_to_normalized_score = get_normalized_score(reaction_to_score)

    write_out_reaction_to_score(reaction_to_score, reaction_to_normalized_score, penalty_exchange, reaction_score_file)