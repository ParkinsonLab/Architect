from argparse import ArgumentParser
from framed import io
from framed import save_sbml_model
from framed import load_cbmodel
from framed import FBA, FVA
from framed import essential_reactions
import utils

MODEL_NUM = 1
NON_ZERO_MIN = 0.00000001


def is_blocked(bounds):

    lb, ub = bounds[0], bounds[1]
    return (abs(lb) < NON_ZERO_MIN) and (abs(ub) < NON_ZERO_MIN)


def is_essential(bounds):

    lb, ub = bounds[0], bounds[1]
    return (lb > NON_ZERO_MIN) or (ub < -1 * NON_ZERO_MIN)
    

def find_active_and_essential_reactions(model, curr_obj_percent, non_zero_min):
    
    active_reactions = set()
    found_essential_reactions = set()
    rxn_to_bounds = FVA(model, obj_percentage=curr_obj_percent) #, reactions=list(remaining_reax))
    for rxn, bounds in rxn_to_bounds.items():
        if is_blocked(bounds):
            continue
        active_reactions.add(rxn)
        if is_essential(bounds):
            found_essential_reactions.add(rxn)
    print (len(active_reactions), len(found_essential_reactions))
    return active_reactions, found_essential_reactions


def write_split_objective(reaction_equation, bounds, writer):

    temp_objectives = []
    rxn_to_info = {}
    if "-->" in reaction_equation:
        metabolite_parts = reaction_equation.split("-->")[0]
    else:
        metabolite_parts = reaction_equation.split("<->")[0]
    for elem in metabolite_parts.split():
        if elem == "+" or utils.is_num(elem):
            continue
        rxn_name = "R_arch_nec_import_" + elem
        temp_objective = "TEMP_obj_" + elem
        temp_objectives.append(temp_objective)
        added_string = "\t".join([temp_objective + ":", elem + " -->", "[0, 1000]"])
        rxn_to_info[temp_objective] = "\t".join([rxn_name + ":", elem + " -->", "[-1000, 0]"])
        writer.write(added_string + "\n")
    return temp_objectives, rxn_to_info


def set_temp_objective(model, temp_objectives, curr_obj_index):

    new_model = model.copy()
    curr_obj_name = temp_objectives[curr_obj_index]
    for r_id, reaction in new_model.reactions.items():
        if r_id == curr_obj_name:
            reaction.objective = 1
        elif r_id in temp_objectives:
            reaction.lb = 0
            reaction.ub = 0
    return new_model


def augmented_with_metabolites_not_produced(high_confidence_file, objective_function, output_file, temp_output_file):

    # 1. Write out without the objective function and write out the objective function separately as well.
    temp_objectives = []
    rxn_to_info = {}
    metabolic_transporters = []
    with open(high_confidence_file) as reader:
        with open(temp_output_file, "w") as temp_writer:
            with open(output_file, "w") as writer:
                for line in reader:
                    line = line.strip()
                    if line == "":
                        continue
                    reaction = line.split(":")[0]
                    if reaction == objective_function:
                        rxn_eqn = line.split(":")[1].split("[")[0]
                        bounds = "[" + line.split("[")[1]
                        temp_objectives, rxn_to_info = write_split_objective(rxn_eqn, bounds, temp_writer)
                    else:
                        temp_writer.write(line + "\n")
                    writer.write(line + "\n")

    # 2.  For each metabolite, find out if it can be produced.
    extended_model = utils.read_model_for_simulation(temp_output_file, "")
    with open(output_file, "a") as writer:
        for i, curr_objective in enumerate(temp_objectives):
            curr_extended_model = set_temp_objective(extended_model, temp_objectives, i)
            if not utils.is_functional_model(curr_extended_model):
                writer.write(rxn_to_info[curr_objective] + "\n")

    # 3.  Write model with required additional metabolite transporters that need to be added.
    model_with_required_transporters = utils.read_model_for_simulation(output_file, objective_function)
    return model_with_required_transporters


def write_only_reactions_of_interest(reactions_of_interest, input_file, output_file):

    with open(input_file) as reader:
        with open(output_file, "w") as writer:
            for line in reader:
                line = line.strip()
                if line == "":
                    continue
                curr_rxn = line.split(":")[0]
                if curr_rxn not in reactions_of_interest:
                    continue
                writer.write(line + "\n")


if __name__ == '__main__':

    parser = ArgumentParser(description="Tests that biomass can be produced under current conditions, and reduces"
                                        "gap-filling candidates.")
    parser.add_argument("--output_folder", type=str, help="Folder containing output.")
    parser.add_argument("--user_defined_file", type=str,
                        help="File containing additional reactions that the user defines should be added, including biomass reaction.")
    
    args = parser.parse_args()
    output_folder = args.output_folder
    user_defined_file = args.user_defined_file
    
    all_conf_and_candidate_file = output_folder + "/SIMULATION_augmented_gapfill_candidates.out"
    candidate_reduced_output_file = output_folder + "/SIMULATED_reduced_universe_with_fva.out"

    # Check if we can produce biomass.
    objective_function = utils.find_objective(user_defined_file)
    model = utils.read_model_for_simulation(all_conf_and_candidate_file, objective_function)
    file_for_FVA = all_conf_and_candidate_file
    if not utils.is_functional_model(model):

        print("Model is not functional with gap-filling candidates; transporters need to be added.")
        # Find biomass metabolites that cannot be produced.
        file_for_FVA = output_folder + "/checks/SIMULATION_augmented_with_transporters.out"
        model = augmented_with_metabolites_not_produced(all_conf_and_candidate_file, objective_function, \
            file_for_FVA, output_folder + "/checks/SIMULATION_individual_metabolite_biomass.out")
    else:
        print("Model is functional with gap-filling candidates.")
    # Now, carry on, perform FVA to reduce the number of gap-filling candidates.
    active_reactions, found_essential_reactions = find_active_and_essential_reactions(model, 0.5, NON_ZERO_MIN)
    write_only_reactions_of_interest(active_reactions, file_for_FVA, candidate_reduced_output_file)
    
    essential_rxn_output = output_folder + "/ESSENTIAL_reactions.out"
    write_only_reactions_of_interest(found_essential_reactions, file_for_FVA, essential_rxn_output)
    
    print ("Essential_reactions:", len(found_essential_reactions))
    augmented_high_conf_with_essential = output_folder + "/SIMULATION_high_confidence_reactions_plus_essentials.out"
    write_only_reactions_of_interest(found_essential_reactions, file_for_FVA, augmented_high_conf_with_essential)
    utils.append_default_reactions(augmented_high_conf_with_essential, output_folder + "/SIMULATION_high_confidence_reactions.out")
	
    utils.convert_to_sbml_model(candidate_reduced_output_file, output_folder + "/SIMULATED_reduced_universe_with_fva.xml")
    utils.convert_to_sbml_model(augmented_high_conf_with_essential, output_folder + "/SIMULATION_high_confidence_reactions_plus_essentials.xml", objective_function)
