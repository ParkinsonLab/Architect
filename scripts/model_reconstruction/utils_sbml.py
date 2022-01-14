import libsbml
import xml.sax.saxutils

def add_metainfo(original_file, output_file, name_of_model, is_kegg, objective_fn, gap_filling_rxns, rxn_to_ec, rxn_to_gene, rxns_of_interest, \
    seq_similarity_reactions, spontaneous_reactions, user_defined_reactions, all_reaction_to_attribute, all_metabolite_to_attribute):
    """This function reads the information in original_file, and modifies it and outputs it to output_file.
    The following additional parameters need to be specified:
    name_of_model: the name of the model.
    is_kegg: True (uses KEGG reaction database) or False (uses BiGG database)
    objective_fn: the name of the objective function for this model.
    gap_filling_rxns: the list of gap-filling reactions.
    rxn_to_ec: mapping of reaction to EC.
    rxn_to_gene: mapping of reaction to gene.
    rxns_of_interest: high-confidence reactions + gap-filling reactions.
    seq_similarity_reactions: reactions that are being added based on sequence similarity (this is for models reconstructed using the BiGG database).
    spontaneous_reactions: reactions that are always added as they are non-enzymatic.
    """

    # Add compartments if this is a BiGG model.
    compart_info = ["<listOfCompartments>"]
    if not is_kegg:
        ids = ["c", "p", "e"]
        names = ["cytosol", "periplasm", "extracellular space"]
    else:
        # Have only one compartment if KEGG.
        ids = ["c"]
        names = ["cytosol"]
    for curr_id, curr_name in zip(ids, names):
        #<compartment id="c" name="cytosol" size="1" constant="true"/>
        curr_string = '<compartment metaid="'+ curr_id + '" id="' + curr_id + '" name="' + curr_name + '" size="1" constant="true"/>'
        compart_info.append(curr_string)
    compart_info.append("</listOfCompartments>")
    add_information_after("<model id=", compart_info, output_file, original_file)

    # Set flux objective
    flux_obj_str_lst = ['<fbc:listOfObjectives fbc:activeObjective="obj">']
    flux_obj_str_lst.append('<fbc:objective fbc:id="obj" fbc:type="maximize">')
    flux_obj_str_lst.append('<fbc:listOfFluxObjectives>')
    flux_obj_str_lst.append('<fbc:fluxObjective fbc:reaction="' + objective_fn + '" fbc:coefficient="1"/>')
    flux_obj_str_lst.append('</fbc:listOfFluxObjectives>')
    flux_obj_str_lst.append('</fbc:objective>')
    flux_obj_str_lst.append('</fbc:listOfObjectives>')
    add_information_after("</listOfReactions>", flux_obj_str_lst, output_file)

    # Set the FBC information on the second line.
    # and change the name of the model.
    line_num_to_new_info = {}
    new_name_of_model = name_of_model
    line_num_to_new_info[2] = '<model metaid="' + new_name_of_model + '" id="' + new_name_of_model + '" fbc:strict="true">'
    new_info = '<sbml xmlns="http://www.sbml.org/sbml/level3/version1/core" ' +\
    'xmlns:fbc="http://www.sbml.org/sbml/level3/version1/fbc/version2" xmlns:groups="http://www.sbml.org/sbml/level3/version1/groups/version1" ' + \
        'level="3" version="1" fbc:required="false" groups:required="false">'
    line_num_to_new_info[1] = new_info
    replace_information(line_num_to_new_info, output_file)

    # Add the compartment for the metabolites if model is made using KEGG.
    if is_kegg:
        change_metabolite_attribute(output_file)

    # Get the lower and upper bounds possible at all.
    bound_to_id, rxn_to_lb, rxn_to_ub = read_bounds(original_file)

    # Then, re-write the file while dispensing of "kineticLaw" parameters 
    # and add the upper and lower bounds to the individual reactions.
    # Also add attributes for each reaction (description/name).
    fix_bounds(output_file, bound_to_id, rxn_to_lb, rxn_to_ub, all_reaction_to_attribute, is_kegg)

    # Add metaId and attributes for each compound (description/name).
    fix_cpd(output_file, all_metabolite_to_attribute, is_kegg)

    # Now, add the reaction to gene association information.
    add_genes_to_file(rxn_to_gene, rxns_of_interest, output_file)

    # Add any pathway information.  Leave out global pathways, as these are generic pathways.
    generic_pathways = ["rn01100", "rn01110", "rn01120", "rn01200", "rn01210", "rn01212", "rn01230", "rn01240", "rn01220"]
    pathwayID_to_name, pathwayID_to_reaction_of_int = get_pathway_to_reaction(all_reaction_to_attribute, rxns_of_interest, is_kegg)
    add_pathway_information(pathwayID_to_name, pathwayID_to_reaction_of_int, generic_pathways, output_file)

    document = libsbml.readSBML(output_file)

    # Add reaction to EC information plus other dblinks
    i = 0
    while i < len(document.model.reactions):
        rxn = document.model.getReaction(i)
        if rxn.id in rxn_to_ec:
            ecs = rxn_to_ec[rxn.id]
            add_annotation_for_rxn(rxn, ecs)

        if rxn.id in gap_filling_rxns:
            add_confidence_for_rxn(rxn, "Gap-filling")
        elif rxn.id in user_defined_reactions:
            add_confidence_for_rxn(rxn, "User-defined reaction")
        elif rxn.id in seq_similarity_reactions:
            add_confidence_for_rxn(rxn, "Non-EC associated reaction added based on sequence similarity")
        elif rxn.id in spontaneous_reactions:
            add_confidence_for_rxn(rxn, "Spontaneous reaction")
        else:
            if rxn.id in rxn_to_ec:
                add_confidence_for_rxn(rxn, "Added due to associated high-confidence EC prediction")

        # Add attributes.
        if is_kegg:
            temp_identifier = rxn.id.split("_")[0]
        else:
            temp_identifier = rxn.id
            if (temp_identifier[-2] == "_") and (temp_identifier[-1].isalpha()):
                temp_identifier = temp_identifier[:-2]
            if temp_identifier.startswith("R_"):
                temp_identifier = temp_identifier[2:]
            # print (temp_identifier)
            # input()
        if temp_identifier in all_reaction_to_attribute:
            # print (all_reaction_to_attribute[temp_identifier])
            curr_dblinks = all_reaction_to_attribute[temp_identifier]["DB_LINKS"]
            add_elem_dblinks(rxn, curr_dblinks)

        i += 1

    # Add metabolite attributes
    i = 0
    while i < len(document.model.species):
        met = document.model.getSpecies(i)
        if is_kegg:
            temp_identifier = met.id.split("[")[0]
        else:
            temp_identifier = met.id
            if (temp_identifier[-2] == "_") and (temp_identifier[-1].isalpha()):
                temp_identifier = temp_identifier[:-2]
            if temp_identifier.startswith("M_"):
                temp_identifier = temp_identifier[2:]
        if temp_identifier in all_metabolite_to_attribute:
            curr_dblinks = all_metabolite_to_attribute[temp_identifier]["DB_LINKS"]
            add_elem_dblinks(met, curr_dblinks)

        i += 1

    libsbml.writeSBML(document, output_file)


def add_to_dict(key_value, key, value):

    if key not in key_value:
        key_value[key] = set()
    key_value[key].add(value)


def add_genes_to_file(rxn_to_gene, rxns_of_interest, output_file):

    all_genes = set()
    gene_to_rxn = {}
    for rxn, curr_genes in rxn_to_gene.items():
        if rxn not in rxns_of_interest:
            continue
        for gene in curr_genes:
            all_genes.add(gene)
            add_to_dict(gene_to_rxn, gene, rxn)

    new_all_genes = all_genes #set()
    new_rxn_to_gene = rxn_to_gene #{}
    # for gene in all_genes:
    #     gene = xml.sax.saxutils.escape(gene)
    #     num_underscores = 1
    #     new_gene = gene.replace("|", "_")
    #     while new_gene in new_all_genes:
    #         num_underscores += 1
    #         new_gene = gene.replace("|", "_"*num_underscores)
    #     new_gene = "G_" + new_gene
    #     new_all_genes.add(new_gene)
    #     rxns_of_int = gene_to_rxn[gene]
    #     for rxn in rxns_of_int:
    #         add_to_dict(new_rxn_to_gene, rxn, new_gene)
    # new_all_genes = sorted(list(new_all_genes))

    # Add the genes associated with each reaction.
    array = []
    with open(output_file) as open_file:
        for line in open_file:
            if line.strip() == "":
                continue
            if line.strip().startswith("<reaction "):
                reaction_id = line.split(" id=")[1].split()[0][1:-1]
                array.append(line)
            elif line.strip() == "</reaction>":
                if reaction_id not in new_rxn_to_gene:
                    array.append(line)
                    continue
                genes = new_rxn_to_gene[reaction_id]
                array = append_rxn_gene_association(array, genes, find_num_space_before(line) + 2)
                array.append(line)
            else:
                array.append(line)
    with open(output_file, "w") as writer:
        for elem in array:
            writer.write(elem)


    # Add all genes in the model.
    array = ["<fbc:listOfGeneProducts>"]
    for gene in new_all_genes:
        string = '<fbc:geneProduct fbc:id="' + gene + '" metaid="' + gene + '" fbc:label="' + gene + '" sboTerm="SBO:0000243"/>'
        array.append(string)
    array.append("</fbc:listOfGeneProducts>")
    add_information_after("</fbc:listOfObjectives>", array, output_file)


def add_pathway_information(pathwayID_to_name, pathwayID_to_reaction_of_int, pathwayIDs_to_ignore, output_file):

    array = ["<groups:listOfGroups>"]
    i = 1
    for pathwayID in sorted(list(pathwayID_to_name.keys())):
        if pathwayID in pathwayIDs_to_ignore:
            continue
        reactions = pathwayID_to_reaction_of_int[pathwayID]
        pathway_name = xml_escape(pathwayID_to_name[pathwayID])
        pathway_intro = '<groups:group sboTerm="SBO:0000633" groups:id="' + pathwayID + '"'
        pathway_intro = pathway_intro + ' groups:name="' + pathway_name + '" groups:kind="partonomy">'
        array.append(pathway_intro)
        array.append("<groups:listOfMembers>")
        for reaction in sorted(list(reactions)):
            array.append('<groups:member groups:idRef="' + reaction + '"/>')
        array.append("</groups:listOfMembers>")
        array.append("</groups:group>")
        i = i + 1
    array.append("</groups:listOfGroups>")
    add_information_after("</fbc:listOfGeneProducts>", array, output_file)


def append_rxn_gene_association(array, genes, num_spaces):

    array.append(" " * num_spaces + "<fbc:geneProductAssociation>\n")
    if len(genes) == 1:
        gene = list(genes)[0]
        string = '<fbc:geneProductRef fbc:geneProduct="' + gene + '"/>'
        array.append(" " * (num_spaces + 2) + string + "\n")
    else:
        array.append(" " * (num_spaces + 2) + "<fbc:or>\n")
        for gene in genes:
            string = '<fbc:geneProductRef fbc:geneProduct="' + gene + '"/>'
            array.append(" " * (num_spaces + 4) + string + "\n")
        array.append(" " * (num_spaces + 2) + "</fbc:or>\n")
    array.append(" " * num_spaces + "</fbc:geneProductAssociation>\n")
    return array


def add_confidence_for_rxn(rxn, curr_note):

    curr_note = "<body xmlns='http://www.w3.org/1999/xhtml'><p>" + curr_note + "</p></body>"
    rxn.appendNotes(curr_note)


def add_annotation_for_rxn(rxn, ecs):

    rxn.metaid = rxn.id
    for ec in ecs:
        cv = libsbml.CVTerm()
        cv.setQualifierType(libsbml.BIOLOGICAL_QUALIFIER)
        cv.setBiologicalQualifierType(libsbml.BQB_IS)
        cv.addResource("http://identifiers.org/ec-code/" + ec)
        rxn.addCVTerm(cv)


def add_elem_dblinks(elem, dblinks):

    if dblinks.strip() == "":
        return
    for dblink in dblinks.split("#"):
        cv = libsbml.CVTerm()
        cv.setQualifierType(libsbml.BIOLOGICAL_QUALIFIER)
        cv.setBiologicalQualifierType(libsbml.BQB_IS)
        cv.addResource("http://identifiers.org/" + dblink)
        elem.addCVTerm(cv)


def xml_escape(string):

    return xml.sax.saxutils.escape(string, entities={"'": "&apos;", "\"": "&quot;"})


def fix_cpd(file_name, all_metabolite_to_attribute, is_kegg):

    array = []
    with open(file_name) as open_file:
        for line in open_file:
            if line.strip().startswith("<species "):
                new_elem = None
                for elem in line.split():
                    if elem.startswith("id="):
                        new_elem = "meta" + elem
                        cpd_identifier = elem.split("=")[1][1:-1]
                        temp_identifier = cpd_identifier
                        if is_kegg:
                            temp_identifier = temp_identifier.split("[")[0]
                        else:
                            if (temp_identifier[-2] == "_") and (temp_identifier[-1].isalpha()):
                                temp_identifier = temp_identifier[:-2]
                            if temp_identifier.startswith("M_"):
                                temp_identifier = temp_identifier[2:]
                        if temp_identifier not in all_metabolite_to_attribute:
                            description = cpd_identifier
                            chemformula = ""
                        else:
                            description = all_metabolite_to_attribute[temp_identifier]["NAME"]
                            chemformula = all_metabolite_to_attribute[temp_identifier]["FORMULA"]
                        if description == "":
                            description = cpd_identifier
                        else:
                            description = description.replace("#", " ")
                            # description = description.split("#")[0]
                            description = xml_escape(description)
                        if chemformula == "":
                            chemformula = ""
                
                # line = find_num_space_before(line) * " " + "<species " + new_elem
                # line = line + ' id="' + cpd_identifier + '" name="' + description + '"'
                # line = line + ' hasOnlySubstanceUnits="true" boundaryCondition="false" constant="false"/>\n'

                line = find_num_space_before(line) * " " + "<species " + new_elem
                line = line + ' id="' + cpd_identifier + '" name="' + description + '"'
                line = line + ' sboTerm="SBO:0000247" hasOnlySubstanceUnits="true" boundaryCondition="false" constant="false"/>\n'
            array.append(line)
    with open(file_name, "w") as writer:
        for elem in array:
            writer.write(elem)


def fix_bounds(output_file, bound_to_id, rxn_to_lb, rxn_to_ub, all_reaction_to_attribute, is_kegg):

    array = []
    start_kinetic = False
    with open(output_file) as open_file:
        for line in open_file:
            if line.strip() == "</listOfSpecies>":
                array.append(line)
                num_space = find_num_space_before(line)
                array.append(num_space * " " + "<listOfParameters>\n")
                for bound, identifier in bound_to_id.items():
                    new_string = (num_space + 2) * " " + '<parameter id="' + identifier + '" '
                    new_string = new_string + 'value="' + str(bound) + '" constant="true"/>\n'
                    array.append(new_string)
                array.append(num_space * " " + "</listOfParameters>\n")
                continue

            if line.strip().startswith("<reaction "):
                new_elems = []
                for i, curr_elem in enumerate(line.strip()[:-1].split()):
                    if i == 0:
                        continue
                    if curr_elem.startswith("id="):
                        curr_identifier = curr_elem.split("=")[1][1:-1]
                        curr_lb = int(rxn_to_lb[curr_identifier])
                        curr_ub = int(rxn_to_ub[curr_identifier])
                        
                        # Get the description out as well.
                        if is_kegg:
                            temp_identifier = curr_identifier.split("_")[0]
                        else:
                            temp_identifier = curr_identifier
                            if (temp_identifier[-2] == "_") and (temp_identifier[-1].isalpha()):
                                temp_identifier = temp_identifier[:-2]
                            if temp_identifier.startswith("R_"):
                                temp_identifier = temp_identifier[2:]
                            
                        if (temp_identifier not in all_reaction_to_attribute):
                            description = curr_identifier
                        else:
                            description = all_reaction_to_attribute[temp_identifier]["NAME"]

                        if description == "":
                            description = curr_identifier
                        else:
                            description = description.replace("#", " ")
                            description = xml_escape(description)
                        
                    if curr_elem.startswith("name="):
                        curr_elem = 'name="' + description + '"'

                    new_elems.append(curr_elem)
                new_elems.append('fbc:lowerFluxBound="' + bound_to_id[curr_lb] + '"')  
                new_elems.append('fbc:upperFluxBound="' + bound_to_id[curr_ub] + '"')  
                line = " " * find_num_space_before(line) + '<reaction metaid="' + curr_identifier + '" ' + " ".join(new_elems) + " sboTerm=\"SBO:0000375\">\n"

            if line.strip().startswith("<kineticLaw>"):
                start_kinetic = True
                continue

            if line.strip().startswith("</kineticLaw>"):
                start_kinetic = False
                continue

            if start_kinetic:
                continue

            array.append(line)

    with open(output_file, "w") as writer:
        for line in array:
            writer.write(line)


def read_bounds(file_name):

    bounds = set()
    reaction_to_lb = {}
    reaction_to_ub = {}
    with open(file_name) as open_file:
        for line in open_file:
            line = line.strip()
            if line == "":
                continue
            if line.startswith("<reaction "):
                for elem in line.split():
                    if elem.startswith("id="):
                        curr_rxn = elem.split("=")[1][1:-1]
            if ("LOWER_BOUND" in line) or ("UPPER_BOUND" in line):
                curr_bound = None
                for elem in line.split():
                    if elem.startswith("value="):
                        elem = elem.split("=")[1]
                        elem = elem.split("/")[0]
                        elem = elem[1:-1]
                        curr_bound = int(elem)
                        bounds.add(curr_bound)
                if ("LOWER_BOUND" in line):
                    reaction_to_lb[curr_rxn] = curr_bound
                else:
                    reaction_to_ub[curr_rxn] = curr_bound
    bound_to_id = {}
    i = 1
    for bound in sorted(bounds):
        bound_to_id[bound] = "FB" + str(i) + "N" + str(abs(bound))
        i += 1
    return bound_to_id, reaction_to_lb, reaction_to_ub


def change_metabolite_attribute(file_name):

    array = []
    with open(file_name) as open_file:
        for line in open_file:
            if line.strip().startswith("<species id="):
                new_elems = []
                for elem in line.strip().split():
                    if elem.startswith("id="):
                        elem = elem[:-1] + '[c]"'
                    if elem.startswith("name="):
                        elem = elem[:-1] + '[c]"'
                    new_elems.append(elem)
                line = " " * find_num_space_before(line) + " ".join(new_elems) + "\n"
            if line.strip().startswith("<speciesReference species="):
                new_elems = []
                for elem in line.strip().split():
                    if elem.startswith("species="):
                        elem = elem[:-1] + '[c]"'
                    new_elems.append(elem)
                line = " " * find_num_space_before(line) + " ".join(new_elems) + "\n"
            array.append(line)
    with open(file_name, "w") as writer:
        for elem in array:
            writer.write(elem)


def get_pathway_to_reaction(all_reaction_to_attribute, rxns_of_interest, is_kegg):

    pathwayID_to_name = {}
    pathwayID_to_reaction_of_int = {}
    for rxn in rxns_of_interest:
        original_rxn = rxn
        if is_kegg:
            rxn = rxn.split("_")[0]
        else:
            if (rxn[-2] == "_") and (rxn[-1].isalpha()):
                rxn = rxn[:-2]
            if rxn.startswith("R_"):
                rxn = rxn[2:]
        if rxn not in all_reaction_to_attribute:
            continue
        pathways_str = all_reaction_to_attribute[rxn]["PATHWAY"]
        if pathways_str == "":
            continue
        for curr_path_info in pathways_str.split("#"):
            pathwayID = curr_path_info.split()[0]
            description = " ".join(curr_path_info.split()[1:])
            pathwayID_to_name[pathwayID] = description
            add_to_dict(pathwayID_to_reaction_of_int, pathwayID, original_rxn)
    return pathwayID_to_name, pathwayID_to_reaction_of_int


def replace_information(line_num_to_new_info, file_name):

    i_to_info = {}
    with open(file_name) as open_file:
        for i, line in enumerate(open_file):
            if i in line_num_to_new_info:
                num_space = find_num_space_before(line)
                line = num_space * " " + line_num_to_new_info[i] + "\n"
            i_to_info[i] = line
    with open(file_name, "w") as writer:
        for i in sorted(i_to_info.keys()):
            info = i_to_info[i]
            writer.write(info)


def add_information_after(text_to_find, array_info_to_add, file_name, input_file=None):

    if input_file is None:
        input_file = file_name
    array = []
    with open(input_file) as open_file:
        prev_line = ""
        for line in open_file:
            array.append(line)
            if line.strip().startswith(text_to_find):
                if not line.strip().startswith("</"):
                    num_spaces = find_num_space_before(line) + 2
                else:
                    num_spaces = find_num_space_before(line)
                prev_elem = None
                for new_elem in array_info_to_add:
                    if prev_elem is not None:
                        if (not prev_elem.strip().endswith("/>")) and (not prev_elem.strip().startswith("</")):
                            num_spaces += 2
                        elif (new_elem.strip().startswith("</")):
                            num_spaces -= 2       
                    array.append(num_spaces * " " + new_elem + "\n")
                    prev_elem = new_elem
            prev_line = line
    with open(file_name, "w") as writer:
        for elem in array:
            writer.write(elem)


def find_num_space_before(line):

    i = 0
    for ch in line:
        if ch == " ":
            i += 1
        else:
            return i
    return i