import parser
from argparse import ArgumentParser
import utils
from framed import essential_reactions
from framed import io

NON_ZERO_MIN = 0.00000001


def load_high_conf_and_candidate_reactions(high_confidence_file, reduced_gap_filling_file, gap_filling_solns, objective_function, temp_output):

    gap_filling_rxns = set()
    for _, values in gap_filling_solns.items():
        for value in values:
            gap_filling_rxns.add(value)

    high_conf_rxn_to_info, _ = utils.read_model_file(high_confidence_file)
    high_conf_rxns = set(high_conf_rxn_to_info.keys())

    rxns_of_interest = high_conf_rxns.union(gap_filling_rxns)

    reduced_candidates_rxn_to_info, _ = utils.read_model_file(reduced_gap_filling_file)
    utils.write_model_with_new_reactions(reduced_candidates_rxn_to_info, {}, temp_output, rxns_of_interest)
    model = utils.read_model_for_simulation(temp_output, objective_function)
    return model, high_conf_rxns

    
def check_sufficiency_and_essentiality_of_gap_fillers(model, gap_filling_solns, high_conf_rxns, output_check):

    writer = open(output_check, "w")
    writer.write("Solution\tIs_Functional\tAll_reactions_essential\n")
    for sol, curr_soln in gap_filling_solns.items():
        new_model = model.copy()
        utils.set_up_model_with_gap_filled_sol(new_model, curr_soln, high_conf_rxns)

        if utils.is_functional_model(new_model):
            is_functional = "Yes"
        else:
            is_functional = "No"

        essential_rxns = set(essential_reactions(new_model, min_growth=NON_ZERO_MIN))
        if curr_soln.issubset(essential_rxns):
            all_essential = "Yes"
        else:
            all_essential = "No"

        writer.write("\t".join([sol, is_functional, all_essential]) + "\n")
    writer.close()


if __name__ == '__main__':

    parser = ArgumentParser(description="Verifies whether each gap-filling solution is necessary and sufficient.")
    parser.add_argument("--output_folder", type=str, help="Folder that contains various output from previous steps.")
    parser.add_argument("--gap_filling_sol_file", type=str, help="File with various gap-filling solutions.")
    parser.add_argument("--user_defined_file", type=str, help="File containing additional reactions that the user defines should be added, including biomass reaction")

    args = parser.parse_args()
    output_folder = args.output_folder
    gap_filling_sol_file = args.gap_filling_sol_file
    user_defined_file = args.user_defined_file

    high_confidence_file = output_folder + "/SIMULATION_high_confidence_reactions_plus_essentials.out"
    reduced_gap_filling_file = output_folder + "/SIMULATED_reduced_universe_with_fva.out"

    # Returns solution ID to reactions involved.
    gap_filling_solns = utils.read_gap_filling_solns(gap_filling_sol_file)

    # What is the objective function (as defined by the user)?
    objective_function = utils.find_objective(user_defined_file)

    # Make mega-network with high-confidence network, and all reactions in candidate gap-filling set.
    output_check = gap_filling_sol_file.split(".out")[0] + "_check_nec_and_suff.out"
    model, high_conf_rxns = load_high_conf_and_candidate_reactions(high_confidence_file, reduced_gap_filling_file, gap_filling_solns, objective_function, \
        output_folder + "/checks/model_test_ess_and_suff.out")
    check_sufficiency_and_essentiality_of_gap_fillers(model, gap_filling_solns, high_conf_rxns, output_check)