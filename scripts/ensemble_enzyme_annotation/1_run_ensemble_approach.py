from argparse import ArgumentParser
import different_ensemble_approaches as ensemble
import glob
import utils


if __name__ == '__main__':

    # Acceptable parameters and arguments for the following methods
    # 1.  method: Majority:
    #           -  arguments: 1, 1.5, 2, 3 or 3.5; high or low
    #           -  default: 2; high
    # 2.  method: EC_specific
    #           -  arguments: all or high
    #           -  default: all
    # 3.  (Default) method: NB
    #           arguments: bernouilli; all or high
    #           default: bernouilli; high
    # 4.  method: Regression
    #           arguments: balanced or not_balanced; l1 or l2
    #           default: not_balanced; l1
    # 5.  method: RF
    #           arguments: balanced, not_balanced or balanced_subsample; ec_specific
    #           default: not_balanced; ec_specific

    methods_of_interest = ["Majority", "EC_specific", "NB", "Regression", "RF"]

    method_to_default = {"Majority": "2/high",
                         "EC_specific": "all",
                         "NB": "bernouilli/high",
                         "Regression": "not_balanced/l1",
                         "RF": "ec_specific/not_balanced"}

    method_to_options = {"Majority": [ ["1", "2", "3", "1.5", "3.5"], ["high", "low"] ],
                         "EC_specific": [ ["all", "high"] ],
                         "NB": [ ["bernouilli"], ["all", "high"] ],
                         "Regression": [ ["balanced", "not_balanced"], ["l1", "l2"] ],
                         "RF": [ ["ec_specific"], ["balanced", "not_balanced", "balanced_subsample"] ]}

    parser = ArgumentParser(description="Runs an ensemble approach of your choosing.")
    parser.add_argument("-i", "--input_file", type=str,
                        help="File where all predictions from the different tools are.", required=True)
    parser.add_argument("-t", "--training_data", type=str,
                        help="Folder where the training data is.", required=True)
    parser.add_argument("-o", "--output_folder", type=str,
                        help="Folder where the predictions are going to be written.", required=True)
    parser.add_argument("-m", "--method", type=str, choices=methods_of_interest, default="NB",
                        help="The ensemble method that you want to run.",)
    parser.add_argument("-a", "--m_arguments", type=str,
                        help="Additional parameters to override default parameters for ensemble method specified.")
    args = parser.parse_args()
    input_file = args.input_file
    training_data = args.training_data
    output_folder = args.output_folder
    method = args.method
    method_arguments = args.m_arguments

    method_arguments = utils.check_and_set_arguments(method, method_arguments, method_to_default, method_to_options)
    tool_to_cutoff_for_high_conf = utils.get_tool_to_cutoff(training_data + "/CUTOFF")
    # Note: trained_models means the obvious thing for NB, LR and RF, but can mean other things for majority rule and
    # EC-specific best tool.
    trained_models, no_fp_ec_to_tool, absent_ecs = ensemble.load_data(training_data, method, method_arguments)
    # only get the high-confidence predictions when asked.
    if (method == "Majority" and "high" in method_arguments) or (method == "NB" and "high" in method_arguments):
        is_high_conf_only = True
    else:
        is_high_conf_only = False
    indiv_predictions = ensemble.load_predictions(input_file, tool_to_cutoff_for_high_conf, method, is_high_conf_only)

    predictable_ecs_file = training_data + "/TOOL_PRED_RANGE/ecs_predictable.out"
    ec_to_predictable_tools = utils.read_ec_to_predictable_tools(predictable_ecs_file)
    ec_to_order_of_labels = {}
    if method in ["NB", "Regression", "RF"]:
        ec_to_order_of_labels = utils.get_order_of_labels(method, ec_to_predictable_tools)
    ensemble_predictions = ensemble.get_ensemble_preds(indiv_predictions, trained_models, method, method_arguments,
                                                       ec_to_predictable_tools, ec_to_order_of_labels, no_fp_ec_to_tool, absent_ecs)
    output_file = output_folder + "/output_" + method + "_" + method_arguments.replace("/", "_") + ".out"
    ensemble.write_out_predictions(ensemble_predictions, no_fp_ec_to_tool, absent_ecs, output_file)