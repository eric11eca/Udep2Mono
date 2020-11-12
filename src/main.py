import os

from polarization import run_polarize_pipeline

datasets = ["sick", "diagnostic", "MED",
            "monotonicity_hard", "monotonicity_simple",
            "boolean", "conditional", "counting", "negation"]
dataset = datasets[0]

if dataset == "sick":  # 1677, 346
    dataset_path = "sick"
elif dataset == "diagnostic":
    dataset_path = "GLUE/glue_data/diagnostic"
elif dataset == "MED":
    dataset_path = "MED"
elif dataset == "monotonicity_hard":
    dataset_path = "SEG/monotonicity_hard"
elif dataset == "monotonicity_simple":
    dataset_path = "SEG/monotonicity_simple"
elif dataset == "boolean":
    dataset_path = "SEG/boolean"
elif dataset == "conditional":
    dataset_path = "SEG/conditional"
elif dataset == "counting":
    dataset_path = "SEG/counting"
elif dataset == "negation":
    dataset_path = "SEG/negation"

in_name = "{}.txt".format(dataset)
val_name = "{}.depccg.parsed.txt".format(dataset)
out_name = "{}.polarized.txt".format(dataset)
incorrect_log_name = "{}.incorrect.txt".format(dataset)
unmatched_log_name = "{}.unmatched.txt".format(dataset)
unmatched_val_name = "{}.unmatched.ccg.txt".format(dataset)
except_log_name = "{}.exception.txt".format(dataset)

path = os.path.join("../data", dataset_path)
in_path = os.path.join(path, in_name)
val_path = os.path.join(path, val_name)
out_path = os.path.join(path, out_name)
incorrect_log_path = os.path.join(path, incorrect_log_name)
unmatched_log_path = os.path.join(path, unmatched_log_name)
unmatched_val_path = os.path.join(path, unmatched_val_name)
exception_log_path = os.path.join(path, except_log_name)

with open(in_path, "r") as data:
    with open(val_path, "r") as annotation:
        lines = data.readlines()
        annotations_val = annotation.readlines()
        annotations, exceptioned, incorrect = run_polarize_pipeline(
            lines, annotations_val, verbose=2, parser="stanford"
        )

        with open(out_path, "w") as correct:
            for sent in annotations:
                correct.write("%s\n" % sent["annotated"])
                correct.write(sent["validation"])
                correct.write("\n")

        with open(incorrect_log_path, "w") as incorrect_log:
            with open(unmatched_val_path, "w") as unmatched_val:
                for sent in incorrect:
                    incorrect_log.write(sent[0])
                    unmatched_val.write(sent[2])

        with open(exception_log_path, "w") as except_log:
            for sent in exceptioned:
                except_log.write(sent[0])
                except_log.write(sent[1])

with open(incorrect_log_path, "r") as incorrect_log:
    with open(unmatched_val_path, "r") as annotation:
        lines = incorrect_log.readlines()
        annotations_val = annotation.readlines()
        annotations, exceptioned, incorrect = run_polarize_pipeline(
            lines, annotations_val, verbose=2, parser="stanza"
        )

        with open(out_path, "a") as correct:
            for sent in annotations:
                correct.write("%s\n" % sent["annotated"])
                correct.write(sent["validation"])
                correct.write("\n")

        with open(unmatched_log_path, "w") as unmatched_log:
            for sent in incorrect:
                # unmatched_log.write(sent[0])
                unmatched_log.write("%s\n" % sent[1])
                #incorrect_log.write("%s\n" % sent[3])
                unmatched_log.write(sent[2])
                #incorrect_log.write("%s\n" % sent[4])
                unmatched_log.write("\n")

        with open(exception_log_path, "w") as except_log:
            for sent in exceptioned:
                except_log.write(sent[0])
                except_log.write(sent[1])
