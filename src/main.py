import os

from polarization import run_polarize_pipeline

datasets = ["sick", "diagnostic"]
dataset = datasets[1]

if dataset == "sick":
    dataset_path = "sick"
elif dataset == "diagnostic":
    dataset_path = "GLUE/glue_data/diagnostic"

in_name = "{}.txt".format(dataset)
val_name = "{}.depccg.parsed.txt".format(dataset)
out_name = "{}.polarized.txt".format(dataset)
incorrect_log_name = "{}.unmatched.txt".format(dataset)
except_log_name = "{}.exception.txt".format(dataset)

path = os.path.join("../data", dataset_path)
in_path = os.path.join(path, in_name)
val_path = os.path.join(path, val_name)
out_path = os.path.join(path, out_name)
incorrect_log_path = os.path.join(path, incorrect_log_name)
exception_log_path = os.path.join(path, except_log_name)

with open(in_path, "r") as data:
    with open(val_path, "r") as annotation:
        lines = data.readlines()
        annotations_val = annotation.readlines()
        annotations, exceptioned, incorrect = run_polarize_pipeline(
            lines, annotations_val, verbose=0
        )

        with open(out_path, "w") as correct:
            for sent in annotations:
                correct.write("%s\n" % sent["annotated"])

        with open(incorrect_log_path, "w") as incorrect_log:
            for sent in incorrect:
                incorrect_log.write(sent[0])
                incorrect_log.write("%s\n" % sent[1])
                incorrect_log.write("%s\n" % sent[3])
                incorrect_log.write(sent[2])
                incorrect_log.write("%s\n" % sent[4])
                incorrect_log.write("%s\n")

        with open(exception_log_path, "w") as except_log:
            for sent in exceptioned:
                except_log.write(sent[0])
                except_log.write(sent[1])
