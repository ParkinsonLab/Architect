from argparse import ArgumentParser
import different_ensemble_approaches as ensemble
import utils
import glob


def get_preds_not_considered(indiv_predictions, tool_to_cutoff_for_high_conf, ecs_with_trained_classifiers, no_fp_ec_to_tool, absent_ecs):

    missed_preds = {}
    for ec, prot_to_tool in indiv_predictions.iteritems():
        if (ec in ecs_with_trained_classifiers) or (ec in no_fp_ec_to_tool) or (ec in absent_ecs):
            continue
        for prot, tool_to_score in prot_to_tool.iteritems():
            for tool, score in tool_to_score.iteritems():
                ensemble.add_indiv_predictions_to_dict(missed_preds, prot, tool, ec, score, None, tool_to_cutoff_for_high_conf, True)
    return missed_preds


def write_indiv_preds_left_out(preds_not_considered, tool_to_cutoff_for_high_conf, output_missed_preds):

    """Write out in the format:
    [TAB]     [TAB]    Tool_1  Tool_2  Tool_3
    Sequence  EC         2        1     0
    where a 2 corresponds to a high-confidence prediction, 1 low-confidence, and 0 not predicted with any level of
    confidence.
    Note that we need to refer to each tool individually to see how big the scores actually are etc."""

    tools_of_interest = sorted(tool_to_cutoff_for_high_conf.keys())

    with open(output_missed_preds, "w") as outfile:
        # First, write the header out.
        outfile.write("KEY\n2: high-confidence prediction\n1: low-confidence prediction\n0: prediction with no confidence\n\n")
        outfile.write("Protein_name\tEC\t")
        for tool in tools_of_interest:
            outfile.write(tool + "\t")
        outfile.write("\n")

        for ec, prot_to_preds in preds_not_considered.iteritems():
            for prot, tool_to_score in prot_to_preds.iteritems():
                string_evidence = get_confidence_to_string_format(tool_to_score, ec, tool_to_cutoff_for_high_conf, tools_of_interest, "2", "1", "0")
                outfile.write(prot + "\t" + ec + "\t" + string_evidence + "\n")


def get_confidence_to_string_format(tool_to_score, ec, tool_to_cutoff_for_high_conf, tools_of_interest, high_conf_str, low_conf_str, no_conf_str):

    string_evidence = []
    if len(tools_of_interest) == 0:
        return ""
    for tool in tools_of_interest:
        if tool not in tool_to_score:
            string_evidence.append(no_conf_str)
        else:
            score = float(tool_to_score[tool])
            if utils.is_high_conf(tool_to_cutoff_for_high_conf, tool, ec, score):
                string_evidence.append(high_conf_str)
            else:
                string_evidence.append(low_conf_str)
    return "\t".join(string_evidence)


if __name__ == '__main__':
    # Acceptable parameters and arguments for the following methods (basically, similar to 1_run_ensemble_approach.py.
    # 1.  method: Majority:
    #           -  arguments: 1, 2 or 3; high or low
    #           -  default: 2; high
    # 2.  method: EC_specific
    #           -  arguments: all or high
    #           -  default: all
    # 3.  method: NB
    #           arguments: bernouilli or binomial; all or high
    #           default: bernouilli; all
    # 4.  method: Regression
    #           arguments: balanced or not_balanced
    #           default: not_balanced
    # 5.  (Default) method: RF
    #           arguments: balanced, not_balanced or balanced_subsample; ec_specific or generic
    #           default: not_balanced; generic

    methods_of_interest = ["Majority", "EC_specific", "NB", "Regression", "RF"]

    method_to_default = {"Majority": "2/high",
                         "EC_specific": "all",
                         "NB": "bernouilli/all",
                         "Regression": "not_balanced",
                         "RF": "ec_specific/not_balanced"}

    method_to_options = {"Majority": [ ["1", "2", "3"], ["high", "low"] ],
                         "EC_specific": [ ["all", "high"] ],
                         "NB": [ ["bernouilli", "binomial"], ["all", "high"] ],
                         "Regression": [ ["balanced", "not_balanced"] ],
                         "RF": [ ["ec_specific", "generic"], ["balanced", "not_balanced", "balanced_subsample"] ]}

    parser = ArgumentParser(description="Runs an ensemble approach of your choosing.")
    parser.add_argument("-i", "--input_file", type=str,
                        help="File where all predictions from the different methods are.", required=True)
    parser.add_argument("-t", "--training_data", type=str,
                        help="Folder where the training data is.", required=True)
    parser.add_argument("-o", "--output_folder", type=str,
                        help="Folder where the predictions are going to be written.", required=True)
    parser.add_argument("-m", "--method", type=str, choices=methods_of_interest, default="RF",
                        help="The ensemble method that you want to run.",)
    parser.add_argument("-a", "--arguments", metavar="N", type=str, nargs="*",
                        help="Additional parameters to override default parameters for ensemble method specified.")
    args = parser.parse_args()
    input_file = args.input_file
    training_data = args.training_data
    output_folder = args.output_folder
    method = args.method
    method_arguments = args.arguments

    method_arguments = utils.check_and_set_arguments(method, method_arguments, method_to_default, method_to_options)
    tool_to_cutoff_for_high_conf = utils.get_tool_to_cutoff(training_data + "/CUTOFF")

    if method == "Majority":
        #print ("Majority rule specified: no ECs left out.")
        exit()

    # One thing I could do is have a reduced version of load_data that only gets the ECs applicable to the data,
    # but that's future work.
    trained_models, no_fp_ec_to_tool, absent_ecs = ensemble.load_data(training_data, method, method_arguments)
    # only get the high-confidence predictions when asked.
    if (method == "NB") and ("high" in method_arguments):
        is_high_conf_only = True
    else:
        is_high_conf_only = False
    indiv_predictions = ensemble.load_predictions(input_file, tool_to_cutoff_for_high_conf, None, is_high_conf_only, True)
    preds_not_considered = get_preds_not_considered\
        (indiv_predictions, tool_to_cutoff_for_high_conf, set(trained_models.keys()), no_fp_ec_to_tool, absent_ecs)
    output_missed_preds = output_folder + "/output_preds_missed_out_" + method + "_" + method_arguments.replace("/", "_")  + ".out"
    write_indiv_preds_left_out(preds_not_considered, tool_to_cutoff_for_high_conf, output_missed_preds)