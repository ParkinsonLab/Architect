from argparse import ArgumentParser
import subprocess
import datetime

def add_to_dict(key_value, key, value):

    if key not in key_value:
        key_value[key] = set()
    key_value[key].add(value)


def get_metanet_to_values(file_name):

    metanet_to_values = {}
    value_to_metanet = {}
    with open(file_name) as open_file:
        for line in open_file:
            line = line.strip()
            if (line == "") or (line[0] == "#"):
                continue
            split = line.split("\t")
            elem = split[0]
            metanet = split[1]
            if metanet == "EMPTY":
                continue
            if "secondary/obsolete/fantasy identifier" in line:
                continue
            add_to_dict(metanet_to_values, metanet, elem)
            add_to_dict(value_to_metanet, elem, metanet)
    open_file.close()
    return metanet_to_values, value_to_metanet


def write_out_rxn_info(output, value_to_metanet, metanet_to_values, prefix_to_name_identifiers_dot_org):

    with open(output, "w") as writer:
        for value, metanet_id in value_to_metanet.items():
            curr_prefix = value.split(":")[0]
            if curr_prefix not in prefix_to_name_identifiers_dot_org:
                continue
            curr_prefix_identifiers_dot_org = prefix_to_name_identifiers_dot_org[curr_prefix]
            metanet_id = list(metanet_id)[0] # Each value cannot have more than one ID associated with it.
            other_values = metanet_to_values[metanet_id]
            for other_value in other_values:
                if (other_value == value) or (other_value == (curr_prefix_identifiers_dot_org + ":" + value.split(":")[1])):
                    continue
                if "R:" in other_value: #Redundant information.
                    continue
                if ("bigg" in other_value) and (":R_" in other_value):
                    continue
                if other_value == metanet_id:
                    continue
                if other_value.startswith("mnx:"):
                    continue
                writer.write("\t".join([value, other_value]) + "\n")
            writer.write("\t".join([value, "metanetx.reaction:" + metanet_id]) + "\n")


def write_out_met_info(output, value_to_metanet, metanet_to_values, prefix_to_name_identifiers_dot_org):

    with open(output, "w") as writer:
        for value, metanet_id in value_to_metanet.items():
            values_encountered = set()
            curr_prefix = value.split(":")[0]
            if curr_prefix not in prefix_to_name_identifiers_dot_org:
                continue
            curr_prefix_identifiers_dot_org = prefix_to_name_identifiers_dot_org[curr_prefix]
            metanet_id = list(metanet_id)[0] # Each value cannot have more than one ID associated with it.
            other_values = metanet_to_values[metanet_id]
            for other_value in other_values:
                if (other_value == value) or (other_value == (curr_prefix_identifiers_dot_org + ":" + value.split(":")[1])):
                    continue
                if "M:" in other_value: #Redundant information.
                    continue
                if ("bigg" in other_value) and (":M_" in other_value):
                    continue
                if other_value == metanet_id:
                    continue
                if other_value.startswith("mnx:"):
                    continue
                if "chebi" in other_value: # Duplicate with CHEBI
                    other_value = "CHEBI:" + other_value.split(":")[1]
                    if other_value in values_encountered:
                        continue
                if other_value.split(":")[0] in ["keggC", "keggD", "keggG", "rheaG"]:
                    continue
                if other_value.split(":")[0] == "slm":
                    other_value = "SLM:" + other_value.split(":")[1]
                    if other_value in values_encountered:
                        continue
                writer.write("\t".join([value, other_value]) + "\n")
                values_encountered.add(other_value)
            writer.write("\t".join([value, "metanetx.chemical:" + metanet_id]) + "\n")


def line_startswith(line, prefixes):

    for prefix in prefixes:
        if line.startswith(prefix):
            return True
    return False

    
def read_dblinks(mapping_output, prefixes_of_interest):

    elem_to_dblinks = {}
    with open(mapping_output) as reader:
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            if not line_startswith(line, prefixes_of_interest):
                continue
            elem = line.split("\t")[0].split(":")[1]
            db_link = line.split("\t")[1]
            add_to_dict(elem_to_dblinks, elem, db_link)
    return elem_to_dblinks


def split_line_by_delim(line, delim):

    split_elems = []
    for elem in line.split(delim):
        split_elems.append(elem.strip())
    return split_elems


def update_kegg_information(input_file, output_file, elem_to_dblinks):

    reader = open(input_file)
    with open(output_file, "w") as writer:
        for i, line in enumerate(reader):
            if i == 0:
                header = ["modified_name", "KEGG_name", "bounds", "db_links"]
                writer.write("\t".join(header) + "\n")
                continue
            if (line.strip() == ""):
                continue
            split_elems = split_line_by_delim(line, "\t")
            rxn = split_elems[0].split("_")[0]
            attributes = ""
            if rxn in elem_to_dblinks:
                attributes = "#".join(sorted(list(elem_to_dblinks[rxn])))
            writer.write("\t".join(split_elems) + "\t" + attributes + "\n")
    reader.close()


def update_bigg_information(input_file, output_file, elem_to_dblinks, header):

    reader = open(input_file)
    with open(output_file, "w") as writer:
        for i, line in enumerate(reader):
            if i == 0:
                writer.write("\t".join(header) + "\n")
                continue
            if line.strip() == "":
                continue
            split_elems = split_line_by_delim(line, "\t")
            rxn = split_elems[0]
            attributes = ""
            if rxn in elem_to_dblinks:
                attributes = "#".join(sorted(list(elem_to_dblinks[rxn])))
            writer.write("\t".join(split_elems) + "\t" + attributes + "\n")
    reader.close()


if __name__ == '__main__':

    parser = ArgumentParser(description="Downloads DB links from MetaNetX.")
    parser.add_argument("-d", "--metanetx_db", type=str,
                        help="Folder where the MetaNetX information will be downloaded.", required=True)
    parser.add_argument("-k", "--kegg_db", type=str,
                        help="Folder where the KEGG information will be downloaded.", required=True)
    parser.add_argument("-b", "--bigg_db", type=str,
                        help="Folder where the BiGG information will be downloaded.", required=True)
    parser.add_argument("-s", "--status_file", type=str, help="File where the status of the information download is written", required=True)
    args = parser.parse_args()
    metanetx_db = args.metanetx_db
    kegg_db = args.kegg_db
    bigg_db = args.bigg_db
    status_file = args.status_file

    writer = open(status_file, "w")
    writer.write(str(datetime.datetime.now()) + ": START downloads for model reconstruction module.\n")

    # Step 1: Download the MetaNetX information.
    url_latest_rxn = "https://beta.metanetx.org/ftp/latest/reac_xref.tsv"
    url_latest_met = "https://beta.metanetx.org/ftp/latest/chem_xref.tsv"
    metanetx_rxn_output = metanetx_db + "/reac_xref.tsv"
    metanetx_met_output = metanetx_db + "/chem_xref.tsv"
    writer.write(str(datetime.datetime.now()) + ": Download reactions dblinks from MetaNetX.\n")
    subprocess.call(["wget", url_latest_rxn, "-O", metanetx_rxn_output, "--no-check-certificate"])
    writer.write(str(datetime.datetime.now()) + ": Download metabolites dblinks from MetaNetX.\n")
    subprocess.call(["wget", url_latest_met, "-O", metanetx_met_output, "--no-check-certificate"])

    # Step 2: Format it to have the KEGG and BiGG information easy to parse.
    writer.write(str(datetime.datetime.now()) + ": Convert information from MetaNetX to be easy to read.\n")
    rxn_mapping_output = metanetx_db + "/PARSED_reaction_mapping.out"
    met_mapping_output = metanetx_db + "/PARSED_metabolite_mapping.out"
    rxn_metanet_to_values, rxn_value_to_metanet = get_metanet_to_values(metanetx_rxn_output)
    met_metanet_to_values, met_value_to_metanet = get_metanet_to_values(metanetx_met_output)
    rxn_prefix_to_name_identifiers_dot_org = {"keggR": "kegg.reaction", "biggR": "bigg.reaction"}
    write_out_rxn_info(rxn_mapping_output, rxn_value_to_metanet, rxn_metanet_to_values, rxn_prefix_to_name_identifiers_dot_org)
    met_prefix_to_name_identifiers_dot_org = {"keggC": "kegg.compound", "keggG": "kegg.glycan", "biggM": "bigg.metabolite"}
    write_out_met_info(met_mapping_output, met_value_to_metanet, met_metanet_to_values, met_prefix_to_name_identifiers_dot_org)

    # Step 3: Update the BiGG and KEGG reaction and metabolite attribute files to have this information.
    writer.write(str(datetime.datetime.now()) + ": Update BiGG metabolites and reactions and KEGG reactions with DBlinks.\n")
    bigg_rxn_to_dblinks = read_dblinks(rxn_mapping_output, ["biggR"])
    bigg_met_to_dblinks = read_dblinks(met_mapping_output, ["biggM"])
    kegg_rxn_to_dblinks = read_dblinks(rxn_mapping_output, ["keggR"])
    update_kegg_information(kegg_db + "/SIMULATION_universe_rxn_before_metanetx.info", \
        kegg_db + "/SIMULATION_universe_rxn.info", kegg_rxn_to_dblinks)
    header_rxn = ["ENTRY", "NAME", "PATHWAY", "DB_LINKS"]
    update_bigg_information(bigg_db + "/attributes_for_rxns_before_metanetx.out", \
        bigg_db + "/attributes_for_rxns.out", bigg_rxn_to_dblinks, header_rxn)
    header_met = ["ENTRY", "NAME", "FORMULA", "PATHWAY", "DB_LINKS"]
    update_bigg_information(bigg_db + "/attributes_for_mets_before_metanetx.out", \
        bigg_db + "/attributes_for_mets.out", bigg_met_to_dblinks, header_met)

    writer.close()