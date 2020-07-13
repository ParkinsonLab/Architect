from argparse import ArgumentParser
import xml.sax.saxutils

def reformat_catfam_results(input_file, output_file, sequence_names):

    new_to_original = {}
    with open(input_file, "r") as reader:
        with open(output_file, "w") as writer:
            for line in reader:
                line = line.strip()
                if line == "":
                    continue
                split = line.split("\t")
                seq, ec = split[0], split[1]
                if ec == "N/A" or not is_eligible_ec(ec):
                    continue
                seq, new_to_original = get_seq_name(sequence_names, seq, new_to_original)
                writer.write(seq + "\t" + ec + "\t1\n")


def reformat_detect_results(input_file, output_file, sequence_names):

    new_to_original = {}
    with open(input_file, "r") as reader:
        with open(output_file, "w") as writer:
            for line in reader:
                line = line.strip()
                if line == "":
                    continue
                split = line.split("\t")
                seq, ec, score = split[0], split[1], split[2]
                if not is_eligible_ec(ec):
                    continue
                seq, new_to_original = get_seq_name(sequence_names, seq, new_to_original)
                writer.write(seq + "\t" + ec + "\t" + score + "\n")


def reformat_eficaz_results(input_file, output_file, sequence_names):

    new_to_original = {}
    with open(input_file, "r") as reader:
        with open(output_file, "w") as writer:
            for line in reader:
                line = line.strip()
                if line == "":
                    continue

                # Ignore 3EC and no EC assignment.
                if line.find("3EC") != -1 or line.find("No EFICAz EC assignment") != -1:
                    continue

                # Is the score low-confidence or high-confidence?
                if line.find("Caution: LOW CONFIDENCE prediction!") != -1:
                    score = "0.5"
                else:
                    score = "1"

                seq = line.split(",")[0]
                ec = line.split(":")[1].split(",")[0].strip()
                if not is_eligible_ec(ec):
                    continue
                seq, new_to_original = get_seq_name(sequence_names, seq, new_to_original)
                writer.write(seq + "\t" + ec + "\t" + score + "\n")


def reformat_enzdp_results(input_file, output_file, sequence_names):

    new_to_original = {}
    with open(input_file, "r") as reader:
        with open(output_file, "w") as writer:
            for line in reader:
                line = line.strip()
                if line == "":
                    continue
                split = line.split()
                seq, ec, score = split[0], split[1], split[2]
                if not is_eligible_ec(ec):
                    continue
                seq, new_to_original = get_seq_name(sequence_names, seq, new_to_original)
                writer.write(seq + "\t" + ec + "\t" + score + "\n")


def add_to_dict_max_prob(ec_to_prob, curr_ec, prob):

    if curr_ec not in ec_to_prob:
        ec_to_prob[curr_ec] = float(prob)
    else:
        max_prob = max(ec_to_prob[curr_ec], float(prob))
        ec_to_prob[curr_ec] = max_prob


def reformat_priam_results(input_file, output_file, sequence_names):

    new_to_original = {}
    curr_seq = ""
    with open(input_file, "r") as reader:
        with open(output_file, "w") as writer:
            for line in reader:
                line = line.strip()
                if line == "" or line[0] == "#":
                    continue
                if line[0] == ">":
                    # If we have seen the results for this sequence, write it out.
                    if curr_seq != "":
                        for ec, prob in ec_to_prob.iteritems():
                            # print curr_seq
                            # print new_to_original
                            curr_seq, new_to_original = get_seq_name(sequence_names, curr_seq, new_to_original)
                            writer.write(curr_seq + "\t" + ec + "\t" + str(prob) + "\n")
                    # In case the sequence name in the file name contained spaces, the space was replaced by #.
                    # Therefore, we here remove any #.
                    curr_seq = line[1:]
                    curr_seq = curr_seq.split("#")[0]
                    ec_to_prob = {}
                else:
                    split = line.split()
                    curr_ec = split[0]
                    prob = split[1]
                    add_to_dict_max_prob(ec_to_prob, curr_ec, prob)

            # Write the results for the last entry into the file.
            for ec, prob in ec_to_prob.iteritems():
                curr_seq, new_to_original = get_seq_name(sequence_names, curr_seq, new_to_original)
                writer.write(curr_seq + "\t" + ec + "\t" + str(prob) + "\n")


def is_eligible_ec(ec):

    split = ec.split(".")
    if len(split) != 4:
        return False
    for elem in split:
        if is_not_num(elem):
            return False
    return True


def is_not_num(elem):

    try:
        int(elem)
        return False
    except ValueError:
        return True


def get_sequence_names_from_file(fasta_file):

    sequence_names = set()
    with open(fasta_file) as in_file:
        for line in in_file:
            line = line.strip()
            if line == "" or line[0] != ">":
                continue
            seq_name = line[1:]
            sequence_names.add(seq_name)
    return sequence_names


def get_seq_name(sequence_names, seq_name_of_int, new_to_original={}):

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


def main():

    parser = ArgumentParser(description="Formats the results from each of your tools to a common format.")
    parser.add_argument("--output_folder", type=str, help="Folder where the formatted results will be written.", required=True)
    parser.add_argument("--fasta_file", type=str, help="The fasta file containing the sequences for which we have"
                                                       " predictions from various tools.", required=True)
    parser.add_argument("--catfam_raw", type=str, help="Path to the raw results from CatFam.")
    parser.add_argument("--detect_raw", type=str, help="Path to the raw results from DETECT.")
    parser.add_argument("--eficaz_raw", type=str, help="Path to the raw results from EFICAz.")
    parser.add_argument("--enzdp_raw", type=str, help="Path to the raw results from EnzDP.")
    parser.add_argument("--priam_raw", type=str, help="Path to the raw results from PRIAM.")

    args = parser.parse_args()
    output_folder = args.output_folder
    fasta_file = args.fasta_file
    sequence_names = get_sequence_names_from_file(fasta_file)

    # Reformat CatFam results.
    if args.catfam_raw:
        reformat_catfam_results(args.catfam_raw, output_folder + "/FORMATTED_CatFam_results.out", sequence_names)

    # Reformat DETECT results.
    if args.detect_raw:
        reformat_detect_results(args.detect_raw, output_folder + "/FORMATTED_DETECT_results.out", sequence_names)

    # Reformat EFICAz results.
    if args.eficaz_raw:
        reformat_eficaz_results(args.eficaz_raw, output_folder + "/FORMATTED_EFICAz_results.out", sequence_names)

    # Reformat EnzDP results.
    if args.enzdp_raw:
        reformat_enzdp_results(args.enzdp_raw, output_folder + "/FORMATTED_EnzDP_results.out", sequence_names)

    # Reformat PRIAM results.
    if args.priam_raw:
        reformat_priam_results(args.priam_raw, output_folder + "/FORMATTED_PRIAM_results.out", sequence_names)


if __name__ == '__main__':

    main()