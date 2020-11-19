import cPickle
import glob
import utils
import math


def get_most_support(ec_tools, argument, ec_to_predictable_tools, max_num_tools=5):
    """
    scheme=1: if at least 3 tools agree, take the prediction.
    scheme=2: take the EC agreed by most tools.
    scheme=3: take an EC only if agreed upon by all tools.
    """

    if "1.5" in argument:
        scheme = 1.5
    elif "3.5" in argument:
        scheme = 3.5
    elif "1" in argument:
        scheme = 1
    elif "2" in argument:
        scheme = 2
    else:
        scheme = 3

    most_supported_labels = {}
    if scheme == 1:
        for ec, tools in ec_tools.items():
            if len(tools) < math.ceil(float(max_num_tools) / 2.0):
                continue
            most_supported_labels[ec] = len(tools)
    elif scheme == 2:
        freq_to_ec = {}
        for ec, tools in ec_tools.items():
            freq = len(tools)
            if freq not in freq_to_ec:
                freq_to_ec[freq] = []
            freq_to_ec[freq].append(ec)
        max_freq = max(freq_to_ec.keys())
        for ec in freq_to_ec[max_freq]:
            most_supported_labels[ec] = max_freq
    elif scheme == 3:
        for ec, tools in ec_tools.items():
            if len(tools) == max_num_tools:
                most_supported_labels[ec] = max_num_tools
    elif scheme == 1.5:
        for ec, tools in ec_tools.items():
            num_of_pred_tools = len(ec_to_predictable_tools[ec]) * 1.0
            if len(tools) < math.ceil(num_of_pred_tools / 2.0):
                continue
            most_supported_labels[ec] = len(tools)
    elif scheme == 3.5:
        for ec, tools in ec_tools.items():
            num_of_pred_tools = len(ec_to_predictable_tools[ec])
            if len(tools) == num_of_pred_tools:
                most_supported_labels[ec] = len(tools)

    return most_supported_labels


def load_best_tools(training_data, method_arguments):

    ec_to_best_tools = {}
    if method_arguments == "all":
        keywords_of_int = ["High_confidence", "Low_confidence"]
    else:
        keywords_of_int = ["High_confidence"]
    with open(training_data) as infile:
        for line in infile:
            line = line.strip()
            if line == "":
                continue
            split = line.split()
            ec, tool, keyword = split[0], split[1], split[2]
            if keyword in keywords_of_int:
                utils.add_to_dict(ec_to_best_tools, ec, tool)
    return ec_to_best_tools


def load_pickled_classifier(folder_name, no_fp_file, no_tp_file):

    file_names = glob.glob(folder_name + "/*")
    ec_to_pickled_classifiers = {}

    for file_name in file_names:

        if file_name.find(".pkl") == -1:
            continue
        ec = ""
        string_split = file_name.split(".pkl")[0].split(".")
        ec = ".".join([string_split[-4][-1], string_split[-3], string_split[-2], string_split[-1]])
        input = open(file_name, 'rb')
        ec_to_pickled_classifiers[ec] = cPickle.load(input)
        input.close()

    no_fp_ec_to_tool = get_list_of_no_fp_ecs(no_fp_file)
    absent_ecs = get_list_of_absent_ecs(no_tp_file)

    return ec_to_pickled_classifiers, no_fp_ec_to_tool, absent_ecs


def get_list_of_no_fp_ecs(file_name):

    ec_to_tool = {}
    with open(file_name) as open_file:
        for i, line in enumerate(open_file):
            line = line.strip()
            if line == "" or i == 0:
                continue
            ec = line.split()[0]
            tools = line.split()[3].split("|")
            ec_to_tool[ec] = tools
    return ec_to_tool


def get_list_of_absent_ecs(file_name):

    absent_ecs = set()
    with open(file_name) as open_file:
        for i, line in enumerate(open_file):
            line = line.strip()
            if i == 0 or line == "":
                continue
            split = line.split()
            absent_ecs.add(split[0])
        open_file.close()
    return absent_ecs


def add_indiv_predictions_to_dict(indiv_predictions, protein, tool, ec, score, method, tool_to_cutoff_for_high_conf, readable=False):
    '''Add entry into dictionary of format:
        {ec1: {protein1: {T1: score, T2: score ....}, protein2: {T3: score}}
        ec2: ...}'''

    if not readable:
        tools = utils.get_modified_tool_name(method, tool_to_cutoff_for_high_conf, tool, ec, score)
    else:
        tools = [tool]

    for tool in tools:
        if ec not in indiv_predictions:
            indiv_predictions[ec] = {protein: {tool: score}}
        elif protein not in indiv_predictions[ec]:
            indiv_predictions[ec][protein] = {tool: score}
        else:
            indiv_predictions[ec][protein][tool] = score


def add_ensemble_predictions_to_dict(ensemble_predictions, protein, ec, score):
    '''Add predictions from ensemble classifier to this dictionary in this format:
        {ec1: {protein1: score, protein2: score, ...},
        ec2: {protein2: score, ...}}.'''

    if ec not in ensemble_predictions:
        ensemble_predictions[ec] = {protein: score}
    else:
        ensemble_predictions[ec][protein] = score


def convert_to_sequence_to_ec_tools(indiv_predictions):
    '''Take as input a dictionary of the format {ec: {protein: {tool: score}}} and output a dictionary of the format
    {seq: {ec: (tool: score) } }'''

    seq_to_ec_tools = {}
    for ec, protein_to_tool in indiv_predictions.items():
        for protein, tools in protein_to_tool.items():
            if protein not in seq_to_ec_tools:
                seq_to_ec_tools[protein] = {ec: tools}
            else:
                seq_to_ec_tools[protein][ec] = tools
    return seq_to_ec_tools


def load_data(training_data, method, method_arguments):

    # No data needs to be loaded for the majority rule.
    if method == "Majority":
        if ("1.5" in method_arguments) or ("3.5" in method_arguments):
            return utils.read_ec_to_predictable_tools(training_data + "/TOOL_PRED_RANGE/ecs_predictable.out"), {}, []
        else:
            return [], {}, []
    # Load the best method(s) per EC.
    if method == "EC_specific":
        ec_to_best_methods = load_best_tools(training_data + "/EC_specific/details_conf.out", method_arguments)
        return ec_to_best_methods, {}, []
    # Load the pickled classifiers otherwise.
    if "high" in method_arguments and method == "NB":
        no_fp_file = training_data + "/NO_NEG_EGS/ecs_of_interest_only_tp_maybe_fn_high.out"
        no_tp_file = training_data + "/NO_NEG_EGS/ecs_of_interest_only_fn_or_fp_high.out"
    else:
        no_fp_file = training_data + "/NO_NEG_EGS/ecs_of_interest_only_tp_maybe_fn_all.out"
        no_tp_file = training_data + "/NO_NEG_EGS/ecs_of_interest_only_fn_or_fp_all.out"
    ec_to_pickled_classifier, no_fp_ec_to_tool, absent_ecs = \
        load_pickled_classifier(training_data + "/" + method + "/" + method_arguments, no_fp_file, no_tp_file)
    return ec_to_pickled_classifier, no_fp_ec_to_tool, absent_ecs


def get_seq_name(split):

    seq_name = split[0]
    i = 1
    while i < len(split) - 3:
        seq_name = seq_name + "\t" + split[i]
        i += 1
    return seq_name


def load_predictions(input_file, tool_to_cutoff_for_high_conf, method, is_high_conf_only=False, readable=False, min_cutoff=0.0001):
    '''Load predictions from file written in the format:
        protein [TAB] Tool [TAB] EC [TAB] score
    and output a dictionary with predictions of the format:
        {ec1: {protein1: {M1: score, M2: score ....}, protein2: {M3: score}}
        ec2: ...}'''

    indiv_predictions = {}
    with open(input_file) as infile:
        for line in infile:
            line = line.strip()
            if line == "":
                continue
            split = line.split("\t")
            protein, tool, ec, score = get_seq_name(split), split[-3], split[-2], float(split[-1])
            if score < min_cutoff:
                continue
            # Only take the high-confidence prediction if specified as such.
            if is_high_conf_only and not utils.is_high_conf(tool_to_cutoff_for_high_conf, tool, ec, score):
                continue
            add_indiv_predictions_to_dict(indiv_predictions, protein, tool, ec, score, method, tool_to_cutoff_for_high_conf, readable)
    return indiv_predictions


def get_feature_vector(order_of_labels, tools, classifier_type):

    feature_vector = []
    if classifier_type == "NB" or classifier_type == "Regression":
        for label in order_of_labels:
            if label in tools:
                feature_vector.append(1)
            else:
                feature_vector.append(0)

    if classifier_type == "RF":
        # hard-coding the length of the feature vector for now because it is the
        # easiest thing to do.
        feature_vector = [0] * 5
        for tool in tools:
            coords = order_of_labels[tool]
            index, value = coords[0], coords[1]
            feature_vector[index] = value

    return feature_vector


def get_ensemble_preds(indiv_predictions, trained_models, method, method_arguments, order_of_labels=[],
                       no_fp_ec_to_tool={}, absent_ecs=[]):
    '''Return a dictionary of the consolidated results of the following format:
    {ec1: {protein1: score, protein2: score}, ec2: {protein2: score, protein3: score} ... }'''

    # This is what we actually want to return.
    ensemble_predictions = {}

    # Majority rule
    # The 'score' returned here is actually the number of tools predicting the EC.
    if method == "Majority":
        seq_to_ec_tool = convert_to_sequence_to_ec_tools(indiv_predictions)
        for seq, ec_tools in seq_to_ec_tool.items():
            most_supported_labels = get_most_support(ec_tools, method_arguments, trained_models)
            for ec, num_support in most_supported_labels.items():
                add_ensemble_predictions_to_dict(ensemble_predictions, seq, ec, num_support)
        return ensemble_predictions

    # EC-specific rule.
    if method == "EC_specific":
        ec_to_best_tools = trained_models
        seq_to_ec_tool = convert_to_sequence_to_ec_tools(indiv_predictions)
        for seq, ec_to_tools in seq_to_ec_tool.items():
            for ec, predicted_tools in ec_to_tools.items():
                if ec not in ec_to_best_tools:
                    continue
                best_tools = ec_to_best_tools[ec]
                for predicted_tool in predicted_tools:
                    if predicted_tool in best_tools:
                        add_ensemble_predictions_to_dict(ensemble_predictions, seq, ec, 'NA')
                        break
        return ensemble_predictions

    # Use pickled classifier for the following methods: Naive Bayes, Regression, Random forest.
    ec_to_pickled_classifiers = trained_models
    for ec, prot_to_tool in indiv_predictions.items():

        # Only negative examples.
        if ec in absent_ecs:
            for prot in prot_to_tool:
                add_ensemble_predictions_to_dict(ensemble_predictions, prot, ec, -1)
            continue

        # no negative examples found while training for this EC.
        if ec in no_fp_ec_to_tool:
            curr_tools_for_ec = no_fp_ec_to_tool[ec]
            for prot, tools_for_prot in prot_to_tool.items():
                if not is_subset(curr_tools_for_ec, tools_for_prot):
                    continue
                add_ensemble_predictions_to_dict(ensemble_predictions, prot, ec, 1.0)
            continue
        # no classifier for this EC and not the special case where no negative example was found for this EC.
        if ec not in ec_to_pickled_classifiers:
            continue
        classifier = ec_to_pickled_classifiers[ec]
        feature_vectors = []
        proteins = []
        for prot, tools in prot_to_tool.items():
            proteins.append(prot)
            feature_vector = get_feature_vector(order_of_labels, tools, method)
            feature_vectors.append(feature_vector)

        predictions = classifier.predict_proba(feature_vectors)
        for prot, prediction, fv in zip(proteins, predictions, feature_vectors):
            zero_prob = prediction[0]
            one_prob = prediction[1]
            add_ensemble_predictions_to_dict(ensemble_predictions, prot, ec, one_prob)
    return ensemble_predictions


def is_subset(tools_for_ec, tools_for_prot):

    for tool in tools_for_prot:
        if tool.split("_")[0] in tools_for_ec:
            return True
    return False


def write_out_predictions(ensemble_predictions, no_fp_ec_to_tool, absent_ecs, output_file):
    '''Write ensemble predictions out to the output file specified, where the ensemble predictions are given in a dict:
        {ec1: {protein1: score, protein2: score, ...},
        ec2: {protein2: score, ...}}.
    The output looks like:
        ec1 [TAB] protein1 [TAB} score
        ec1 [TAB] protein2 [TAB] score ...
    In addition, if the EC is one without any false positive predictions or without any true positive examples, we
    add a note to the following effect (resp.)
        ec1 [TAB] protein1 [TAB} score [TAB] No false positives while training for this EC
        ec1 [TAB] protein2 [TAB] score [TAB] No true positive examples while training for this EC'''

    with open(output_file, "w") as outfile:
        for ec, protein_to_score in ensemble_predictions.items():

            if ec in no_fp_ec_to_tool:
                for protein, score in protein_to_score.items():
                    line = "\t".join([ec, protein, str(score), "No false positives while training for this EC"])
                    outfile.write(line + "\n")

            elif ec in absent_ecs:
                for protein, score in protein_to_score.items():
                    line = "\t".join([ec, protein, str(score), "No true positive examples while training for this EC"])
                    outfile.write(line + "\n")

            else:
                for protein, score in protein_to_score.items():
                    line = "\t".join([ec, protein, str(score)])
                    outfile.write(line + "\n")