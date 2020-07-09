from framed import FBA, FVA, io, read_cbmodel_from_file
KEY_EQUATION = 'reaction.equation'
KEY_LB = 'reaction.lb'
KEY_UB = 'reaction.ub'

NON_ZERO_MIN = 0.00000001

def is_num(string):

    try:
        float(string)
        return True
    except ValueError:
        return False


def append_default_reactions(output_filename, input_file, contains_biomass=False):

    with open(output_filename, "a") as writer:
        with open(input_file) as reader:
            for line in reader:
                line = line.strip()
                if line == "":
                    continue
                if contains_biomass:
                    line = line.split("#")[0].strip()
                writer.write(line + "\n")
                
                
def read_model_file(file_name, rxns_to_ignore=None):
    '''Return 1. {reaction: {EQUATION: value, LB: value, UB: value}}
              2. {metabolite: set(rxn_1, rxn_2, ...)}
    Ignore those reactions if provided by the user (a set).
    '''

    rxn_to_info = {}
    metabolite_to_rxn = {}

    open_file = open(file_name)

    for line in open_file:
        line = line.strip()
        if line == "":
            continue

        reaction_name = line.split(":")[0]
        if rxns_to_ignore is not None and reaction_name in rxns_to_ignore:
            continue

        split = line.split("\t")
        equation = split[1]
        bounds_info = split[2].strip()[1:-1].split(",")
        
        if bounds_info[0] != "":
            lb = float(bounds_info[0])
        else:
            lb = 0
            
        if bounds_info[1] != "":
            ub = float(bounds_info[1])
        else:
            ub = 0

        rxn_to_info[reaction_name] = {KEY_EQUATION: equation, KEY_LB: lb, KEY_UB: ub}
        update_metabolite_to_rxn(metabolite_to_rxn, reaction_name, equation)

    open_file.close()

    return rxn_to_info, metabolite_to_rxn
    
    
def update_metabolite_to_rxn(metabolite_to_rxn, reaction_name, equation):

    split = equation.split()
    for elem in split:
        if elem in ['<->', '-->', '+'] or is_num(elem):
            continue
        add_to_dict(metabolite_to_rxn, elem, reaction_name)
        
        
def add_to_dict(key_value, key, value, need_values_in_set=True):

    if not need_values_in_set:
        key_value[key] = value
    else:
        if key not in key_value:
            s = set()
            s.add(value)
            key_value[key] = s
        else:
            key_value[key].add(value)
    
    
def write_model_with_new_reactions(candidate_rxn_to_info, new_reactions_to_info, output_filename, rxns_of_interest=None):

    # First, write the information about the candidate reactions that we could be adding.
    writer = open(output_filename, "w")
    for reaction_name in sorted(candidate_rxn_to_info):
        if (rxns_of_interest is not None) and (reaction_name not in rxns_of_interest):
            continue
        info = candidate_rxn_to_info[reaction_name]
        equation, lb, ub = info[KEY_EQUATION], info[KEY_LB], info[KEY_UB]
        writer.write(reaction_name + ":\t" + equation + "\t[" + str(lb) + ", " + str(ub) + "]\n")

    # Now, add the new reaction information.
    for reaction_name in sorted(new_reactions_to_info):
        if (rxns_of_interest is not None) and (reaction_name not in rxns_of_interest):
            continue
        info = new_reactions_to_info[reaction_name]
        equation, lb, ub = info[KEY_EQUATION], info[KEY_LB], info[KEY_UB]
        writer.write(reaction_name + ":\t" + equation + "\t[" + str(lb) + ", " + str(ub) + "]\n")

    writer.close()
    
    
def set_compartment(model):
    for met in model.metabolites:
        curr_obj = model.metabolites[met]
        curr_obj.compartment = '[c]'


def set_objective(model, objective_reaction):
    for r_id, reaction in model.reactions.items():
        if r_id == objective_reaction:
            reaction.objective = 1

def read_model_for_simulation(input_file, objective_function):

    model = read_cbmodel_from_file(input_file)
    set_compartment(model) # set metabolites by default in cytoplasm
    set_objective(model, objective_function)

    return model
    
    
def find_objective(user_defined_file):

    objective_function = ""
    with open(user_defined_file) as open_file:
        for line in open_file:
            line = line.strip()
            if line == "":
                continue
            if "#True" in line:
                objective_function = line.split(":")[0]
                break
    return objective_function
    
    
def set_up_model_with_gap_filled_sol(model, gap_filling_rxns, high_conf_rxns):
    """Keep only reactions in high_conf_rxns and in gap_filling_rxns active."""

    rxns_of_interest = gap_filling_rxns.union(high_conf_rxns)
    for r_id, reaction in model.reactions.items():
        if r_id in rxns_of_interest:
            continue
        reaction.lb = 0
        reaction.ub = 0
        
        
def is_functional_model(model):

    solution = FBA(model)
    return solution.fobj > NON_ZERO_MIN