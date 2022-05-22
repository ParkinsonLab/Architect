from os import replace
from framed import FBA, FVA, io, read_cbmodel_from_file, save_sbml_model
import xlsxwriter
import subprocess
import xml.sax.saxutils

KEY_EQUATION = 'reaction.equation'
KEY_LB = 'reaction.lb'
KEY_UB = 'reaction.ub'

NON_ZERO_MIN = 0.00000001

HEADERS_rxn_excel = {}
HEADERS_rxn_excel['Abbreviation'] = 0
HEADERS_rxn_excel['Description'] = 1
HEADERS_rxn_excel['Reaction'] = 2
HEADERS_rxn_excel['GPR'] = 3
HEADERS_rxn_excel['Genes'] = 4
HEADERS_rxn_excel['Proteins'] = 5
HEADERS_rxn_excel['Subsystem'] = 6
HEADERS_rxn_excel['Reversible'] = 7
HEADERS_rxn_excel['Lower bound'] = 8
HEADERS_rxn_excel['Upper bound'] = 9
HEADERS_rxn_excel['Objective'] = 10
HEADERS_rxn_excel['Confidence'] = 11
HEADERS_rxn_excel['EC Number'] = 12
HEADERS_rxn_excel['Notes'] = 13
HEADERS_rxn_excel['References'] = 14
REV_HEADERS_rxn_excel = {}
for k, v in HEADERS_rxn_excel.items():
    REV_HEADERS_rxn_excel[v] = k

HEADERS_met_excel = {}
HEADERS_met_excel['Abbreviation'] = 0
HEADERS_met_excel['Description'] = 1
HEADERS_met_excel['Neutral formula'] = 2
HEADERS_met_excel['Charged formula'] = 3
HEADERS_met_excel['Charge'] = 4
HEADERS_met_excel['Compartment'] = 5
HEADERS_met_excel['KEGG ID'] = 6
HEADERS_met_excel['PubChem ID'] = 7
HEADERS_met_excel['ChEBI ID'] = 8
HEADERS_met_excel['InChI string'] = 9
HEADERS_met_excel['SMILES'] = 10
HEADERS_met_excel['HMDB ID'] = 11


def is_num(string):

    try:
        float(string)
        return True
    except ValueError:
        return False


def append_default_reactions(output_filename, input_file, contains_biomass=False, exchange_rxns_of_interest=None):

    with open(output_filename, "a") as writer:
        with open(input_file) as reader:
            for line in reader:
                line = line.strip()
                if line == "":
                    continue
                if contains_biomass:
                    line = line.split("#")[0].strip()
                
                # Do something if there are exchange reactions of interest to look at.
                if (exchange_rxns_of_interest is not None):
                    curr_rxn = line.split(":")[0]
                    if is_exchange_rxn(curr_rxn):
                        equation = line.split("\t")[1]
                        first_part_of_line = curr_rxn + ":\t" + equation
                        if curr_rxn in exchange_rxns_of_interest:
                            line = first_part_of_line + "\t[-10, 1000]"
                        else:
                            line = first_part_of_line + "\t[0, 1000]"
                writer.write(line + "\n")
                
                
def read_model_file(file_name, rxns_to_ignore=None, exchange_rxns_of_interest=None):
    '''Return 1. {reaction: {EQUATION: value, LB: value, UB: value}}
              2. {metabolite: set(rxn_1, rxn_2, ...)}
    Ignore those reactions if provided by the user (a set).
    If exchange reactions are provided, then, constrain the exchange reactions alone to be active.
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

        if (exchange_rxns_of_interest is not None) and (is_exchange_rxn(reaction_name)):
            if reaction_name in exchange_rxns_of_interest:
                lb = -10
            else:
                lb = 0

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
    
    
def add_to_dict_max_score(key_score, key, score):

    if key not in key_score:
        key_score[key] = score
    else:
        current_max = key_score[key]
        key_score[key] = max(current_max, score)


def add_to_dict_key_score_value(key_score_value, key, score, value):

    if key not in key_score_value:
        key_score_value[key] = {}
    if score not in key_score_value[key]:
        key_score_value[key][score] = set()
    key_score_value[key][score].add(value)
    
    


def write_model_with_new_reactions(candidate_rxn_to_info, new_reactions_to_info, output_filename, rxns_of_interest=None):

    # First, write the information about the candidate reactions that we could be adding.
    writer = open(output_filename, "w")
    already_written = set()
    for reaction_name in sorted(candidate_rxn_to_info):
        if (rxns_of_interest is not None) and (reaction_name not in rxns_of_interest):
            continue
        info = candidate_rxn_to_info[reaction_name]
        equation, lb, ub = info[KEY_EQUATION], info[KEY_LB], info[KEY_UB]
        writer.write(reaction_name + ":\t" + equation + "\t[" + str(lb) + ", " + str(ub) + "]\n")
        already_written.add(reaction_name)

    # Now, add the new reaction information.
    for reaction_name in sorted(new_reactions_to_info):
        if reaction_name in already_written:
            continue
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


def convert_to_sbml_model(input_file, output_xml_file, objective_function=""):

    model = read_model_for_simulation(input_file, objective_function)
    save_sbml_model(model, output_xml_file)	


def read_gap_filling_solns(gap_filling_solns_file):

    solnID_to_reactions = {}
    with open(gap_filling_solns_file) as reader:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            split = line.split()
            solnID = split[0]
            reactions = set(split[1:])
            add_to_dict(solnID_to_reactions, solnID, reactions, False)
    return solnID_to_reactions


def modify_arrow(string):

    if "<->" in string:
        return string.replace("<->", "->")
    else:
        return string.replace("-->", "->")


def is_reversible(lb, ub):

    return (lb < 0) and (ub > 0)


def read_mapping_of_rxn_to_ec(high_confidence_rxn_to_ec_file, low_confidence_rxn_to_ec_file, complete_mapping_file):
    """First read the high-confidence reaction to EC, then the low-confidence ones, 
    then for remaining reactions from the complete mapping file"""

    rxn_to_ec = {}

    # Get high-confidence reactions first.
    with open(high_confidence_rxn_to_ec_file) as reader:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            split = line.split()
            ec, rxn = split[0], split[1]
            add_to_dict(rxn_to_ec, rxn, ec)

    # Get low-confidence reactions now.
    with open(low_confidence_rxn_to_ec_file) as reader:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            split = line.split()
            ec, rxn = split[0], split[1]
            add_to_dict(rxn_to_ec, rxn, ec)

    reactions_already_covered = set(rxn_to_ec.keys())

    # Get mapping for remaining reactions now.
    with open(complete_mapping_file) as reader:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            split = line.split()
            ec, rxn = split[1], split[0]
            if rxn in reactions_already_covered:
                continue
            add_to_dict(rxn_to_ec, rxn, ec)
    
    return rxn_to_ec


def read_mapping_of_rxn_to_gene(rxn_to_ec, output_folder, performed_blastp):

    rxn_to_gene = {}

    ec_to_gene = {}
    ec_to_gene_file = output_folder + "/ec_to_gene_not_final.out"
    with open(ec_to_gene_file) as open_file:
        for line in open_file:
            line = line.strip()
            if line == "":
                continue
            split = line.split("\t")
            ec = split[0]
            gene = "\t".join(split[1:])
            add_to_dict(ec_to_gene, ec, gene)
    for rxn, ecs in rxn_to_ec.items():
        for ec in ecs:
            if ec not in ec_to_gene:
                continue
            genes = ec_to_gene[ec]
            for gene in genes:
                add_to_dict(rxn_to_gene, rxn, gene)

    if performed_blastp:
        rxn_to_gene_file = output_folder + "/rxn_to_gene_blast_not_final.out"
        with open(rxn_to_gene_file) as open_file:
            for line in open_file:
                line = line.strip()
                if line == "":
                    continue
                split = line.split("\t")
                rxn = split[0]
                gene = "\t".join(split[1:])
                add_to_dict(rxn_to_gene, rxn, gene)

    return rxn_to_gene


def read_info_for_excel_format(file_name, abbrev_rxn_to_all_info=None, all_mets_to_info=None):

    if (abbrev_rxn_to_all_info is None):
        abbrev_rxn_to_all_info = {}
    if (all_mets_to_info is None):
        all_mets_to_info = {}
    
    rxn_to_info, met_to_info = read_model_file(file_name)
    for abbrev_rxn in sorted(rxn_to_info.keys()):
        info_read = rxn_to_info[abbrev_rxn]
        info_xl = {}
        info_xl["Abbreviation"] = abbrev_rxn
        info_xl["Reaction"] = modify_arrow(info_read[KEY_EQUATION])
        info_xl["Reversible"] = is_reversible(info_read[KEY_LB], info_read[KEY_UB])
        info_xl["Lower bound"] = info_read[KEY_LB]
        info_xl["Upper bound"] = info_read[KEY_UB]
        info_xl["Objective"] = 0 # default
        info_xl["Notes"] = "" # default
        info_xl["EC Number"] = "" # default
        abbrev_rxn_to_all_info[abbrev_rxn] = info_xl
    for met, info in met_to_info.items():
        if met not in all_mets_to_info:
            all_mets_to_info[met] = set()
        for rxn in info:
            all_mets_to_info[met].add(rxn)

    return abbrev_rxn_to_all_info, all_mets_to_info


def convert_mapping_gene_name_to_compatible(old_rxn_to_gene):

    old_gene_names = set()
    for genes in old_rxn_to_gene.values():
        for gene in genes:
            old_gene_names.add(gene)
    old_to_new_gene_name = convert_gene_names_to_compatible(old_gene_names)

    new_rxn_to_gene = {}
    for rxn, genes in old_rxn_to_gene.items():
        for old_gene in genes:
            new_gene = old_to_new_gene_name[old_gene]
            add_to_dict(new_rxn_to_gene, rxn, new_gene)
    return new_rxn_to_gene


def convert_gene_names_to_compatible(gene_names):

    change_char_list = ["|", " ", "=", "+", "'", '"', "`"]
    old_to_new_gene_name = {}
    new_all_genes = set()
    for old_gene_name in gene_names:
        new_gene_name = ""
        for ch in old_gene_name:
            if not str.isalnum(ch):
                ch = "_"
            new_gene_name = new_gene_name + ch
        # new_gene_name = xml.sax.saxutils.escape(old_gene_name)
        # for curr_ch in change_char_list:
        #     new_gene_name = replace_with_underscore(new_gene_name, curr_ch, new_all_genes)
        new_all_genes.add(new_gene_name)
        old_to_new_gene_name[old_gene_name] = "G_" + new_gene_name
    return old_to_new_gene_name


def replace_with_underscore(old_name, character, all_new_names):

    num_underscores = 1
    new_name = old_name.replace(character, "_")
    while new_name in all_new_names:
        num_underscores += 1
        new_name = old_name.replace(character, "_"*num_underscores)
    return new_name

    
def read_split_components(line, delim):

    split_components_before = line.split(delim)
    split_components_after = []
    for component in split_components_before:
        component = component.strip()
        split_components_after.append(component)
    return split_components_after


def read_header(line, delim):

    index_to_header = {}
    split_headers = read_split_components(line, delim)
    for i, header in enumerate(split_headers):
        index_to_header[i] = header
    return index_to_header


def read_attributes_file(filename):

    element_to_info = {}
    with open(filename) as reader:
        for i, line in enumerate(reader):
            if i == 0:
                index_to_header = read_header(line, "\t")
                continue
            if line.strip() == "":
                continue
            split_components = read_split_components(line, "\t")
            element = split_components[0]
            element_to_info[element] = {}
            for j, component in enumerate(split_components):
                if j == 0:
                    continue
                header = index_to_header[j]
                element_to_info[element][header] = component
    return element_to_info


def update_with_additional_attributes(abbrev_to_info_xls, attributes_folder, is_bigg):

    # Step 1: read the attributes for reactions and metabolites.
    all_reaction_to_attribute = read_attributes_file(attributes_folder + "/attributes_for_rxns.out")
    all_metabolite_to_attribute = read_attributes_file(attributes_folder + "/attributes_for_mets.out")

    # Step 2: add the reaction-specific information to abbrev_to_info_xls.
    for rxn, info in abbrev_to_info_xls.items():
        if is_bigg:
            if (rxn[-2] == "_") and (rxn[-1].isalpha()):
                rxn = rxn[:-2]
            if rxn.startswith("R_"):
                rxn = rxn[2:]
        else:
            rxn = rxn.split("_")[0]
        if rxn not in all_reaction_to_attribute:
            continue
        attribute_to_values = all_reaction_to_attribute[rxn]
        # Fix the names
        info["Description"] = attribute_to_values["NAME"]
        info["Subsystem"] = attribute_to_values["PATHWAY"]

    return all_reaction_to_attribute, all_metabolite_to_attribute


def write_excel_model_gapfilled(abbrev_to_info_xls, all_metabolite_to_attribute, is_bigg, high_confidence_and_ess_reactions, gap_filling_rxns, objective_function, \
    metabolite_to_info, rxn_to_ec, rxn_to_gene, seq_similarity_reactions, spontaneous_rxns, user_defined_rxns, output_file):

    # Set up the objective function.
    abbrev_to_info_xls[objective_function]["Objective"] = 1

    # Set up the gap-filling reactions.
    for rxn in gap_filling_rxns:
        abbrev_to_info_xls[rxn]["Notes"] = "Gap-filling"

    # Set up the spontaneous reactions.
    for rxn in spontaneous_rxns:
        abbrev_to_info_xls[rxn]["Notes"] = "Spontaneous/non-enzymatic"

    # Reactions of interest
    rxns_of_interest = set()
    for rxn in high_confidence_and_ess_reactions:
        rxns_of_interest.add(rxn)
    for rxn in gap_filling_rxns:
        rxns_of_interest.add(rxn)

    # Set up the EC information where applicable.
    for rxn, ecs in rxn_to_ec.items():
        if (rxn not in rxns_of_interest):
            continue
        abbrev_to_info_xls[rxn]["EC Number"] = ";".join(sorted(ecs))

    # Mark reactions added via sequence similarity as so.
    for rxn in seq_similarity_reactions:
        if rxn in rxn_to_ec:
            continue
        abbrev_to_info_xls[rxn]["Notes"] = "Added to high-confidence network due to sequence similarity (reaction has no EC)."

    # Add a note for reactions added and defined by the user.
    for rxn in user_defined_rxns:
        abbrev_to_info_xls[rxn]["Notes"] = "User-defined reactions"

    # Add the reaction to gene information.
    for rxn, genes in rxn_to_gene.items():
        genes = sorted(list(genes))
        if (rxn not in rxns_of_interest):
            continue
        abbrev_to_info_xls[rxn]["GPR"] = " or ".join(genes)
        abbrev_to_info_xls[rxn]["Genes"] = ";".join(genes)

    info_rxn_sheet = {}

    # Header for reaction sheet.
    for header, index in HEADERS_rxn_excel.items():
        info_rxn_sheet["0_" + str(index)] = header
    j = 0
    for abbrev in sorted(abbrev_to_info_xls.keys()):
        if (abbrev not in rxns_of_interest):
            continue
        j += 1
        info = abbrev_to_info_xls[abbrev]
        for k, header in REV_HEADERS_rxn_excel.items():
            if header not in info:
                continue
            info_rxn_sheet[str(j) + "_" + str(k)]= info[header]

    info_met_sheet = {}

    # Header for metabolite sheet.
    descrip_i = HEADERS_met_excel["Description"]
    formula_i = HEADERS_met_excel["Neutral formula"]
    for header, index in HEADERS_met_excel.items():
        info_met_sheet["0_" + str(index)] = header
    i = 0
    for metabolite in sorted(metabolite_to_info.keys()):
        corresponding_rxns = metabolite_to_info[metabolite]
        if len(corresponding_rxns.intersection(rxns_of_interest)) == 0:
            continue
        i += 1
        info_met_sheet[str(i) + "_0"] = metabolite
        if is_bigg:
            if metabolite.startswith("M_"):
                metabolite = metabolite[2:]
            if (metabolite[-2] == "_") and (metabolite[-1].isalpha()):
                metabolite = metabolite[:-2]
        if metabolite not in all_metabolite_to_attribute:
            continue
        info_met_sheet[str(i) + "_" + str(descrip_i)] = all_metabolite_to_attribute[metabolite]["NAME"]
        info_met_sheet[str(i) + "_" + str(formula_i)] = all_metabolite_to_attribute[metabolite]["FORMULA"]


    workbook = xlsxwriter.Workbook(output_file)
    update_excel_info(workbook, "Reaction List", info_rxn_sheet)
    update_excel_info(workbook, "Metabolite List", info_met_sheet)
    workbook.close()


def update_excel_info(workbook, ws_name, info):
    """Update information in open workboox in sheet ws_name.  The information is given in the 
    dictionary info in the format
    {"x_y": "value"}
    such that the value is written in row x and column y.
    """

    worksheet = workbook.add_worksheet(ws_name)
    for location, value in info.items():
        row = int(location.split("_")[0])
        col = int(location.split("_")[1])
        worksheet.write(row, col, value)


def perform_blastp_and_find_additional_reactions(fasta_file, database_bigg, reaction_no_ec_to_gene_file, blast_output, output_file, max_evalue):

    # Step 1: Perform blastp.
    subprocess.call(["diamond", "blastp", "--db", database_bigg, "--query", fasta_file, "--out", blast_output, "-f", "6"])

    # Step 2: Get the significant hits.
    genes_with_significant_hits = parse_out_blast_output(blast_output, max_evalue)

    # Step 3: Get the corresponding reactions.
    reactions_to_add = set()
    subset_reaction_to_gene = {}
    gene_to_reaction = read_bigg_gene_to_reaction(reaction_no_ec_to_gene_file)
    for gene in genes_with_significant_hits:
        if gene not in gene_to_reaction:
            continue
        corresponding_reactions = gene_to_reaction[gene]
        query_genes = genes_with_significant_hits[gene]
        for rxn in corresponding_reactions:
            reactions_to_add.add(rxn)
            for gene in query_genes:
                add_to_dict(subset_reaction_to_gene, rxn, gene)

    # Step 4: Write out the reactions.
    with open(output_file, "w") as writer:
        writer.write("#The following reactions are not associated with any EC and are added based on sequence similarity alone.\n")
        for rxn in reactions_to_add:
            genes = subset_reaction_to_gene[rxn]
            writer.write(rxn + "\t" + ";".join(list(genes)) + "\n")
    return reactions_to_add


def read_bigg_gene_to_reaction(file_name):

    gene_to_reaction = {}
    with open(file_name) as reader:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            split = line.split()
            rxn = split[0]
            genes = split[1].split(";")
            for gene in genes:
                add_to_dict(gene_to_reaction, gene, rxn)
    return gene_to_reaction


def parse_out_blast_output(blast_output, max_evalue):

    db_gene_to_query = {}
    with open(blast_output) as reader:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            split = line.split("\t")
            query = split[0]
            db_gene = split[1]
            evalue = float(split[-2])
            if evalue > max_evalue:
                continue
            add_to_dict(db_gene_to_query, db_gene, query)
    return db_gene_to_query


def get_seq_name(sequence_names, seq_name_of_int, new_to_original={}):
    """Copied from 0_format_raw_results.py from Architect\scripts\ensemble_enzyme_annotation.  
    In future, will make sure no copy."""

    seq_name_of_int = xml.sax.saxutils.unescape(seq_name_of_int, {"&apos;": "'", "&quot;": '"'})
    if len(new_to_original) != 0:
        if seq_name_of_int in new_to_original:
            return new_to_original[seq_name_of_int], new_to_original

    if seq_name_of_int in sequence_names:
        return seq_name_of_int, new_to_original

    num_variations = 2
    num_var = 1
    # Try different kinds of dictionaries
    while num_var <= num_variations:
        new_to_original = get_new_to_original(sequence_names, num_var)
        if seq_name_of_int in new_to_original:
            return new_to_original[seq_name_of_int], new_to_original
        num_var += 1

    # This is a last case resort.
    for curr_seq_name in sequence_names:
        if curr_seq_name.find(seq_name_of_int) != -1:
            return curr_seq_name, new_to_original


def get_new_to_original(sequence_names, num_var):
    """Also copied from 0_format_raw_results.py from Architect\scripts\ensemble_enzyme_annotation.  
    In future, will make sure no copy."""

    new_to_original = {}

    # Sequence names are written such that the first of a space delimited set of characters is written.
    if num_var == 1:
        for seq_name in sequence_names:
            first = seq_name.split()[0]
            new_to_original[first] = seq_name
        return new_to_original

    # ...written such that the second element of a "|" delimited set of characters is written.
    if num_var == 2:
        for seq_name in sequence_names:
            if len(seq_name.split("|")) < 2:
                return {}
            second = seq_name.split("|")[1]
            new_to_original[second] = seq_name
        return new_to_original


def is_exchange_rxn(reaction_name):

    return reaction_name.startswith("R_EX_")


def get_cpd_to_exchange_rxns_for_media(media_path, chosen_media):

    exchange_rxns_of_interest = set()
    with open(media_path) as open_file:
        for line in open_file:
            line = line.strip()
            if line == "":
                continue
            split = line.split("\t")
            curr_media, cpd = split[0], split[2]
            if curr_media != chosen_media:
                continue
            exchange_rxn = "R_EX_" + cpd + "_e" #eg: R_EX_ac_e
            exchange_rxns_of_interest.add(exchange_rxn)
    return exchange_rxns_of_interest