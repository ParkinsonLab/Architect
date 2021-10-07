import parser
from argparse import ArgumentParser
import utils, utils_sbml
from framed import essential_reactions
from framed import io
import os

NON_ZERO_MIN = 0.00000001


def output_sbml_models(high_confidence_and_ess_file, reduced_gap_filling_file, essential_gap_fillers, gap_filling_solns, \
    objective_function, is_kegg, rxn_to_ec, rxn_to_gene, seq_similarity_reactions, spontaneous_reactions, user_defined_reactions, \
        temp_dir, all_reaction_to_attribute, all_metabolite_to_attribute, output_xml_folder, num_output_models):

    temp_output = temp_dir + "/model.out"

    high_conf_rxn_to_info, _ = utils.read_model_file(high_confidence_and_ess_file)
    high_conf_rxns = set(high_conf_rxn_to_info.keys())

    if num_output_models > len(gap_filling_solns):
        print ("Architect WARNING: you have fewer gap-filling solutions than you wish output models for.")

    reduced_candidates_rxn_to_info, _ = utils.read_model_file(reduced_gap_filling_file)

    i = 0
    while i < min(len(gap_filling_solns), num_output_models):
        key = "Sol_" + str(i)
        gap_filling_rxns = gap_filling_solns[key]
        gap_filling_rxns = gap_filling_rxns.union(essential_gap_fillers)

        rxns_of_interest = high_conf_rxns.union(gap_filling_rxns)

        utils.write_model_with_new_reactions(reduced_candidates_rxn_to_info, high_conf_rxn_to_info, temp_output, rxns_of_interest)
        utils.convert_to_sbml_model(temp_output, output_xml_folder + "/model_with_sol_" + str(i) + "_unannotated.xml", objective_function)
        utils_sbml.add_metainfo(output_xml_folder + "/model_with_sol_" + str(i) + "_unannotated.xml", output_xml_folder + "/model_with_sol_" + str(i) + "_annotated.xml", \
            "Architect_model_" + str(i), is_kegg, objective_function, gap_filling_rxns, rxn_to_ec, rxn_to_gene, rxns_of_interest, \
                seq_similarity_reactions, spontaneous_reactions, user_defined_reactions, all_reaction_to_attribute, all_metabolite_to_attribute)
        i += 1


def output_excel_models(high_confidence_and_ess_reactions, abbrev_to_info_xls, all_metabolite_to_attribute, is_bigg, \
    essential_gap_fillers, gap_filling_solns, spontaneous_rxns, objective_function, metabolite_to_info, \
        rxn_to_ec, rxn_to_gene, seq_similarity_reactions, user_defined_rxns, output_folder, num_output_models):

    i = 0
    while i < min(len(gap_filling_solns), num_output_models):
        key = "Sol_" + str(i)
        gap_filling_rxns = gap_filling_solns[key]
        gap_filling_rxns = gap_filling_rxns.union(essential_gap_fillers)

        output_file = output_folder + "/model_with_sol_" + str(i) + ".xlsx"
        utils.write_excel_model_gapfilled(abbrev_to_info_xls, all_metabolite_to_attribute, is_bigg, high_confidence_and_ess_reactions, gap_filling_rxns, objective_function, \
            metabolite_to_info, rxn_to_ec, rxn_to_gene, seq_similarity_reactions, spontaneous_rxns, user_defined_rxns, output_file)
        i += 1


def read_blastp_reax(file_name):

    blastp_reactions = set()
    with open(file_name) as reader:
        for line in reader:
            line = line.strip()
            if (line == "") or (line[0] == "#"):
                continue
            rxn = line.split()[0]
            blastp_reactions.add(rxn)
    return blastp_reactions


if __name__ == '__main__':

    parser = ArgumentParser(description="Constructs a metabolic model based on output from gap-filling.")
    parser.add_argument("--output_folder", type=str, help="Folder that contains various output from previous steps.")
    parser.add_argument("--final_output_folder", type=str, help="Folder that contains final output.")
    parser.add_argument("--gap_filling_sol_file", type=str, help="File with various gap-filling solutions.")
    parser.add_argument("--user_defined_file", type=str, help="File containing additional reactions that the user defines should be added, including biomass reaction")
    parser.add_argument("--num_output_models", type=int, help="Number of output models to be written out.")
    parser.add_argument("--database", type=str, help="Folder containing various information.")
    # parser.add_argument("--ec_preds_file", type=str, help="File containing predictions from pipeline")
    # parser.add_argument("--additional_preds_file", type=str, help="File containing additional predictions (from tools and not ensemble classifier)")

    args = parser.parse_args()
    output_folder = args.output_folder
    final_output_folder = args.final_output_folder
    gap_filling_sol_file = args.gap_filling_sol_file
    user_defined_file = args.user_defined_file
    num_output_models = args.num_output_models
    database = args.database
    # enzyme_predictions_file = args.ec_preds_file
    # additional_preds_file = args.additional_preds_file

    high_confidence_file = output_folder + "/SIMULATION_high_confidence_reactions.out"
    high_confidence_and_ess_file = output_folder + "/SIMULATION_high_confidence_reactions_plus_essentials.out"
    reduced_gap_filling_file = output_folder + "/SIMULATED_reduced_universe_with_fva.out"
    
    spontaneous_file = database + "/SIMULATION_spontaneous_or_non_enzymatic.out"
    complete_mapping_file = database + "/reaction_to_ec_no_spont_non_enz_reax.out"
    high_confidence_rxn_to_ec_file = output_folder + "/MAP_high_confidence_reactions.out"
    low_confidence_rxn_to_ec_file = output_folder + "/MAP_low_confidence_reactions.out"

    # Returns solution ID to reactions involved.
    gap_filling_solns = utils.read_gap_filling_solns(gap_filling_sol_file)

    # What is the objective function (as defined by the user)?
    objective_function = utils.find_objective(user_defined_file)

    # What are the user-defined reactions?
    user_defined_rxns_to_info, _ = utils.read_model_file(user_defined_file)
    user_defined_rxns = set(user_defined_rxns_to_info.keys())

    # Get additional information for output in Excel.
    high_conf_rxn_to_info, _ = utils.read_model_file(high_confidence_file)
    high_confidence_reactions = set(high_conf_rxn_to_info.keys())

    # If we are dealing with a database from BiGG, let's make sure we add a note if a reaction is added via sequence similarity.
    seq_similarity_reactions = set()
    performed_blastp = (os.path.split(database)[-1] != "KEGG_universe")
    if performed_blastp:
        seq_similarity_reactions = read_blastp_reax(output_folder + "/blastp_additional_reactions.out")

    abbrev_to_info_xls, mets_to_info = utils.read_info_for_excel_format(high_confidence_and_ess_file)
    high_confidence_and_ess_reactions = set(abbrev_to_info_xls.keys())
    essential_gap_fillers = high_confidence_and_ess_reactions - high_confidence_reactions
    spontaneous_rxn_to_info, _ = utils.read_model_file(spontaneous_file)
    spontaneous_rxns = set(spontaneous_rxn_to_info.keys())

    rxn_to_ec = utils.read_mapping_of_rxn_to_ec(high_confidence_rxn_to_ec_file, low_confidence_rxn_to_ec_file, complete_mapping_file)
    rxn_to_gene = utils.read_mapping_of_rxn_to_gene(rxn_to_ec, output_folder + "/additional", performed_blastp)
    rxn_to_gene = utils.convert_mapping_gene_name_to_compatible(rxn_to_gene)

    # Output Excel model.
    abbrev_to_info_xls, mets_to_info = utils.read_info_for_excel_format(reduced_gap_filling_file, abbrev_to_info_xls, mets_to_info)
    if not performed_blastp:
        attributes_folder = database
    else:
        attributes_folder = os.path.split(database)[0] + "/Common_BiGG_info"
    all_reaction_to_attribute, all_metabolite_to_attribute = utils.update_with_additional_attributes\
        (abbrev_to_info_xls, attributes_folder, performed_blastp)
    output_excel_models(high_confidence_and_ess_reactions, abbrev_to_info_xls, all_metabolite_to_attribute, performed_blastp, \
        essential_gap_fillers, gap_filling_solns, spontaneous_rxns, objective_function, mets_to_info, \
            rxn_to_ec, rxn_to_gene, seq_similarity_reactions, \
            user_defined_rxns, final_output_folder, num_output_models)

    # Output SBML model with high-confidence reactions and gap-filling reactions.
    output_sbml_models(high_confidence_and_ess_file, reduced_gap_filling_file, essential_gap_fillers, gap_filling_solns, \
        objective_function, not performed_blastp, rxn_to_ec, rxn_to_gene, seq_similarity_reactions, spontaneous_rxns, \
            user_defined_rxns, output_folder + "/checks", all_reaction_to_attribute, all_metabolite_to_attribute, \
                final_output_folder, num_output_models)    