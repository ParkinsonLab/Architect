from argparse import ArgumentParser
import different_ensemble_approaches as ensemble
import glob
import utils
import datetime
import os
import shutil


if __name__ == '__main__':

    # Acceptable parameters and arguments for the following methods
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

    method_to_options = {"NB": [ "bernouilli/all", "bernouilli/high" ],
                         "Regression": [ "balanced/l1", "not_balanced/l1", "balanced/l2", "not_balanced/l2" ],
                         "RF": [ "ec_specific/balanced", "ec_specific/not_balanced", "ec_specific/balanced_subsample" ]}

    parser = ArgumentParser(description="Sets up classifiers.")
    parser.add_argument("-t", "--training_data", type=str,
                        help="Folder where the training data is.", required=True)
    parser.add_argument("-s", "--status_file", type=str, help="File where the status of the databases is written", required=True)
    args = parser.parse_args()
    training_data = args.training_data
    status_file = args.status_file

    tool_to_cutoff_for_high_conf = utils.get_tool_to_cutoff(training_data + "/CUTOFF")

    predictable_ecs_file = training_data + "/TOOL_PRED_RANGE/ecs_predictable.out"
    ec_to_predictable_tools = utils.read_ec_to_predictable_tools(predictable_ecs_file)

    actual_annotations = utils.read_actual_annotations(training_data + "/RAW/ALL_actual_file.out")

    writer = open(status_file, "w")

    for method, list_method_arguments in method_to_options.items():

        for method_arguments in list_method_arguments:

            writer.write(str(datetime.datetime.now()) + ": START for " + method + " " + method_arguments + "\n")
            # only get the high-confidence predictions when asked.
            if (method == "NB" and "high" in method_arguments):
                is_high_conf_only = True
            else:
                is_high_conf_only = False
            indiv_predictions = ensemble.load_predictions(training_data + "/RAW/ALL_pred_file.out", tool_to_cutoff_for_high_conf, method, is_high_conf_only)
            trained_models, no_fp_ec_to_tool, absent_ecs = ensemble.load_data(training_data, method, method_arguments)

            ec_to_order_of_labels = {}
            if method in ["NB", "Regression", "RF"]:
                ec_to_order_of_labels = utils.get_order_of_labels(method, ec_to_predictable_tools)

            additional_info = None
            if method == "RF":
                additional_info = utils.load_optimal_rf_settings(training_data + "/RAW/RF/" + method_arguments + ".out")
            elif method == "Regression":
                additional_info = utils.load_regression_param_info(training_data + "/RAW/Regression/params.out")

            output_pickle_folder = training_data + "/" + method + "/" + method_arguments

            if not os.path.exists(output_pickle_folder):
                os.makedirs(output_pickle_folder)
            else:
                shutil.rmtree(output_pickle_folder)
                os.makedirs(output_pickle_folder)

            ensemble.create_classifiers(indiv_predictions, actual_annotations, method, method_arguments, \
                ec_to_predictable_tools, training_data, output_pickle_folder, ec_to_order_of_labels, additional_info)

    writer.write(str(datetime.datetime.now()) + ": Successfully set up all classifiers\n")
    writer.close()