from argparse import ArgumentParser
import urllib #import urllib.request
import x_set_up_metanetx_dblinks as metanetx
import glob
import datetime
import os
import shutil

def read_header(line, delim):

    i_to_header = {}
    split_line = split_line_by_delim(line, delim)
    for i, part in enumerate(split_line):
        i_to_header[i] = part
    return i_to_header


def split_line_by_delim(string, delim):

    split_parts = []
    for elem in string.split(delim):
        split_parts.append(elem.strip())
    return split_parts


def read_elem_to_info(file_name):

    elem_to_info = {}
    with open(file_name) as reader:
        for i, line in enumerate(reader):
            if (line.strip() == ""):
                continue
            if i == 0:
                i_to_header = read_header(line, "\t")
                continue
            split_info = split_line_by_delim(line, "\t")
            key = split_info[0]
            j = 1
            info = {}
            for part in split_info[1:]:
                info[i_to_header[j]] = part
                j += 1
            elem_to_info[key] = info
    return elem_to_info


def get_actual_url(prefix, elems):

    return prefix + "+".join(elems)


def get_dict_from_header(liste):

    d = {}
    for elem in liste:
        d[elem] = []
    return d


def get_info_about_elem(actual_url, header, elem_to_info):

    open_file = urllib.urlopen(actual_url)
    for line in open_file:
        # line = line.decode('utf-8')
        if line.strip() == "":
            continue
        if line.strip() == "///":
            curr_title = ""
            continue
        if line[0] != " ":
            curr_title = line.split()[0]
            if curr_title == "ENTRY":
                curr_entry = line.split()[1]
                elem_to_info[curr_entry] = get_dict_from_header(header)
        if curr_title != "ENTRY":
            if curr_title not in header:
                continue
            curr_string = line[12:].strip()
            elem_to_info[curr_entry][curr_title].append(curr_string)
    open_file.close()


def read_kegg_info(elems_of_int, headers_of_int):

    elems_of_int = sorted(list(elems_of_int))
    unable_to_parse = set()
    all_missing_elem = set()
    elem_to_info = {}
    prefix = "http://rest.kegg.jp/get/"
    i = 0
    while i < len(elems_of_int):
        
        actual_url = get_actual_url(prefix, elems_of_int[i:i + 10])
        try:
            get_info_about_elem(actual_url, headers_of_int, elem_to_info)
        except:
            for elem in elems_of_int[i:i+10]:
                unable_to_parse.add(elem)
        i += 10
        # print (i)
    for elem in elems_of_int:
        if elem not in elem_to_info:
            all_missing_elem.add(elem)
    return elem_to_info, all_missing_elem, unable_to_parse


def format_kegg_rxn(kegg_reactions_to_info):

    kegg_reactions_to_info_formatted = {}
    for rxn, info in kegg_reactions_to_info.items():
        info_formatted = {}
        info_formatted["NAME"] = "#".join(info["NAME"])
        info_formatted["PATHWAY"] = "#".join(info["PATHWAY"])
        info_formatted["ENZYME"] = get_ecs_from_kegg_download(info["ENZYME"])
        info_formatted["EQUATION"] = info["EQUATION"][0]
        kegg_reactions_to_info_formatted[rxn] = info_formatted
    return kegg_reactions_to_info_formatted


def get_ecs_from_kegg_download(list_of_lines):

    ecs = set()
    for line in list_of_lines:
        for elem in line.split():
            if not is_valid_ec(elem):
                continue
            ecs.add(elem)
    return ecs


def is_a_number(string):

    try:
        float(string)
        return True
    except:
        return False

        
def is_valid_ec(string):

    split_elems = string.split(".")
    if len(split_elems) != 4:
        return False
    for elem in split_elems:
        if not is_a_number(elem):
            return False
    return True


def is_reversible(bounds):

    bounds = bounds.replace("[", "")
    bounds = bounds.replace("]", "")
    bounds = bounds.split(",")
    lb, ub = float(bounds[0]), float(bounds[1])
    return (lb < 0) and (ub > 0)


def write_out_kegg_rxn_download(universe_reaction_to_info, kegg_reactions_to_downloaded_info_formatted, missing_kegg_reactions, \
    unable_to_parse_kegg_reactions, EC_output, rxn_attributes, temporary_kegg_universe, unable_to_parse_output):

    # Step 1: let's write out the rxn to EC mapping.
    with open(EC_output, "w") as writer:
        for universe_reaction in universe_reaction_to_info:
            kegg_name = universe_reaction_to_info[universe_reaction]["KEGG_name"]
            if kegg_name not in kegg_reactions_to_downloaded_info_formatted:
                continue
            if "ENZYME" not in kegg_reactions_to_downloaded_info_formatted[kegg_name]:
                continue
            ecs = kegg_reactions_to_downloaded_info_formatted[kegg_name]["ENZYME"]
            for ec in ecs:
                writer.write("\t".join([universe_reaction, ec]) + "\n")

    # Step 2: Write out the reaction attributes.
    with open(rxn_attributes, "w") as writer:
        header = ["ENTRY", "NAME", "PATHWAY", "DB_LINKS"]
        writer.write("\t".join(header) + "\n")
        for _, info_with_db_links in universe_reaction_to_info.items():
            kegg_name = info_with_db_links["KEGG_name"]
            pathway = ""
            description = ""
            if kegg_name in kegg_reactions_to_downloaded_info_formatted:
                if "PATHWAY" in kegg_reactions_to_downloaded_info_formatted[kegg_name]:
                    pathway = kegg_reactions_to_downloaded_info_formatted[kegg_name]["PATHWAY"]
                if "NAME" in kegg_reactions_to_downloaded_info_formatted[kegg_name]:
                    description = kegg_reactions_to_downloaded_info_formatted[kegg_name]["NAME"]
            db_links = info_with_db_links["db_links"]
            writer.write("\t".join([kegg_name, description, pathway, db_links]) + "\n")

    # Step 3: Write out the temporary kegg universe.  
    with open(temporary_kegg_universe, "w") as writer:
        for modified_name, info_with_db_links in universe_reaction_to_info.items():
            kegg_name = info_with_db_links["KEGG_name"]
            if kegg_name not in kegg_reactions_to_downloaded_info_formatted:
                continue
            formula = kegg_reactions_to_downloaded_info_formatted[kegg_name]["EQUATION"]
            bounds_str = info_with_db_links["bounds"]
            if is_reversible(bounds_str):
                formula = formula.replace("<=>", "<->")
            else:
                formula = formula.replace("<=>", "-->")
            writer.write("\t".join([modified_name + ":", formula, bounds_str]) + "\n")

    # Step 4: Write in a separate file saying which files could not be found and for what reason.
    with open(unable_to_parse_output, "w") as writer:
        header = ["Reaction_not_found", "Reason?"]
        writer.write("\t".join(header) + "\n")
        for rxn in missing_kegg_reactions:
            if rxn in unable_to_parse_kegg_reactions:
                writer.write("\t".join([rxn, "URL_not_resolved"]) + "\n")
            else:
                writer.write("\t".join([rxn, "Did_not_find"]) + "\n")


def read_new_rxn_definitions(file_name):

    reaction_to_equation = {}
    with open(file_name) as reader:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            split = line.split("\t")
            rxn, equation = split[0], split[1]
            reaction_to_equation[rxn] = equation
    return reaction_to_equation


def make_substitutions(temporary_kegg_universe, final_kegg_universe, new_reaction_definitions):

    reader = open(temporary_kegg_universe)
    with open(final_kegg_universe, "w") as writer:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            rxn = line.split(":")[0]
            if rxn not in new_reaction_definitions:
                writer.write(line + "\n")
            else:
                bounds = line.split("\t")[-1]
                new_line = "\t".join([rxn + ":", new_reaction_definitions[rxn], bounds])
                writer.write(new_line + "\n")
    reader.close()


def read_list(file_name):

    liste = set()
    with open(file_name) as reader:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            liste.add(line)
    return liste


def write_out_specific_reactions(output_file, reactions_of_int, universal_reactions_file):

    reaction_to_line = {}
    with open(universal_reactions_file) as reader:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            reaction = line.split(":")[0]
            reaction_to_line[reaction] = line

    with open(output_file, "w") as writer:
        for reaction in reactions_of_int:
            if reaction not in reaction_to_line:
                continue
            line = reaction_to_line[reaction]
            writer.write(line + "\n")


def read_cpds_from_reactions(final_kegg_universe):

    cpd_list = set()
    with open(final_kegg_universe) as reader:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            reaction = line.split("\t")[1].strip()
            reaction = reaction.replace("+", "")
            reaction = reaction.replace("<->", "")
            reaction = reaction.replace("-->", "")
            for elem in reaction.split():
                if is_a_number(elem):
                    continue
                cpd_list.add(elem)
    return cpd_list


def write_out_metabolite_attributes(kegg_cpds_to_downloaded_info, kegg_cpd_to_dblinks, missing_kegg_cpds, unable_to_parse_kegg_cpds, \
        met_attribute_output, unable_to_parse_output):

    # First, write out the information from KEGG, with the database links from MetaNetX also added.
    with open(met_attribute_output, "w") as writer:
        header = ["ENTRY", "NAME", "FORMULA", "PATHWAY", "DB_LINKS"]
        writer.write("\t".join(header) + "\n")
        for kegg_cpd, kegg_downloaded_info in kegg_cpds_to_downloaded_info.items():

            name = "#".join(kegg_downloaded_info["NAME"])
            formula = "#".join(kegg_downloaded_info["FORMULA"])
            pathway = "#".join(kegg_downloaded_info["PATHWAY"])

            db_links = ""
            if kegg_cpd in kegg_cpd_to_dblinks:
                db_links_array = sorted(list(kegg_cpd_to_dblinks[kegg_cpd]))
                db_links = "#".join(db_links_array)

            info = [kegg_cpd, name, formula, pathway, db_links]
            writer.write("\t".join(info) + "\n")

    # Now, write out the compounds for which I could not parse out any information. 
    with open(unable_to_parse_output, "w") as writer:
        header = ["Metabolite_not_found", "Reason?"]
        writer.write("\t".join(header) + "\n")
        for cpd in missing_kegg_cpds:
            if cpd in unable_to_parse_kegg_cpds:
                writer.write("\t".join([cpd, "URL_not_resolved"]) + "\n")
            else:
                writer.write("\t".join([cpd, "Did_not_find"]) + "\n")


if __name__ == '__main__':

    parser = ArgumentParser(description="Sets up KEGG database.")
    parser.add_argument("-k", "--kegg_rxn_db", type=str,
                        help="Folder where the KEGG reaction database is.", required=True)
    parser.add_argument("-m", "--metanetx_db", type=str,
                        help="Folder where the MetaNetX information has been downloaded.", required=True)
    parser.add_argument("-s", "--status_file", type=str, help="File where the status of the databases is written", required=True)
    args = parser.parse_args()
    reaction_db = args.kegg_rxn_db
    metanetx_db = args.metanetx_db
    status_file = args.status_file

    writer = open(status_file, "a")

    # Download name, formula, EC and pathway for each reaction.
    universe_reaction_to_info = read_elem_to_info(reaction_db + "/SIMULATION_universe_rxn.info") 
    kegg_reactions_of_int = set()
    for modified_name, info in universe_reaction_to_info.items():
        kegg_rxn = info["KEGG_name"]
        kegg_reactions_of_int.add(kegg_rxn)
    kegg_rxn_headers = ["NAME", "PATHWAY", "ENZYME", "EQUATION"]
    writer.write(str(datetime.datetime.now()) + ": Download KEGG reaction information.\n")
    kegg_reactions_to_downloaded_info, missing_kegg_reactions, unable_to_parse_kegg_reactions = read_kegg_info(kegg_reactions_of_int, kegg_rxn_headers)

    # Format the information.
    kegg_reactions_to_downloaded_info_formatted = format_kegg_rxn(kegg_reactions_to_downloaded_info)

    # Write out all the downloaded reaction information.
    writer.write(str(datetime.datetime.now()) + ": Write out all the information from KEGG to a temporary 'universe' of reactions.\n")
    EC_output = reaction_db + "/reaction_to_ec_no_spont_non_enz_reax.out"
    rxn_attributes_output = reaction_db + "/attributes_for_rxns.out"
    temporary_kegg_universe = reaction_db + "/TEMP_SIMULATION_universe_rxn.out"
    unable_to_parse_rxn_output = reaction_db + "/DEBUG_unable_to_parse_rxns.out"
    write_out_kegg_rxn_download(universe_reaction_to_info, kegg_reactions_to_downloaded_info_formatted, \
        missing_kegg_reactions, unable_to_parse_kegg_reactions, EC_output, rxn_attributes_output, temporary_kegg_universe, unable_to_parse_rxn_output)

    # Now, make the substitutions for reactions that I have modified.
    writer.write(str(datetime.datetime.now()) + ": Modify reactions from KEGG as per Nirvana's curations.\n")
    substitution_file = reaction_db + "/DIFF_modified_equations.out"
    final_kegg_universe = reaction_db + "/SIMULATION_universe_rxn.out"
    new_reaction_definitions = read_new_rxn_definitions(substitution_file)
    make_substitutions(temporary_kegg_universe, final_kegg_universe, new_reaction_definitions)

    # Write out specific reactions such as spontaneous and non-enzymatic reactions.
    writer.write(str(datetime.datetime.now()) + ": Prepare spontaneous reaction file.\n")
    spontaneous_list = reaction_db + "/SIMULATION_spontaneous_or_non_enzymatic.lst"
    spontaneous_output = reaction_db + "/SIMULATION_spontaneous_or_non_enzymatic.out"
    spontaneous_reactions = read_list(spontaneous_list)
    write_out_specific_reactions(spontaneous_output, spontaneous_reactions, final_kegg_universe)

    # Get the compounds of interest.
    kegg_cpds_of_int = read_cpds_from_reactions(final_kegg_universe)
    kegg_cpd_headers = ["ENTRY", "NAME", "FORMULA", "PATHWAY"]
    writer.write(str(datetime.datetime.now()) + ": Download KEGG compound information.\n")
    kegg_cpds_to_downloaded_info, missing_kegg_cpds, unable_to_parse_kegg_cpds = read_kegg_info(kegg_cpds_of_int, kegg_cpd_headers)
    met_mapping_output = metanetx_db + "/PARSED_metabolite_mapping.out"
    kegg_cpd_to_dblinks = metanetx.read_dblinks(met_mapping_output, ["keggC", "keggG"])
    met_attributes_output = reaction_db + "/attributes_for_mets.out"
    unable_to_parse_met_output = reaction_db + "/DEBUG_unable_to_parse_rxns.out"
    writer.write(str(datetime.datetime.now()) + ": Format KEGG compound attribute file.\n")
    write_out_metabolite_attributes(kegg_cpds_to_downloaded_info, kegg_cpd_to_dblinks, missing_kegg_cpds, unable_to_parse_kegg_cpds, \
        met_attributes_output, unable_to_parse_met_output)

    writer.write(str(datetime.datetime.now()) + ": Successfully set up all databases.")
    writer.close()