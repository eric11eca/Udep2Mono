import os
from util import *
import numpy as np


dataset_path = "gold"
dataset = "gold"
path = os.path.join("../data", dataset_path)
in_name = "{}.polarized.txt".format(dataset)
data_name = "{}.txt".format(dataset)
data_path = os.path.join(path, data_name)
val_name = "{}.label.txt".format(dataset)
in_path = os.path.join(path, in_name)
val_path = os.path.join(path, val_name)
pos_name = "{}.pos.txt".format(dataset)
pos_path = os.path.join(path, pos_name)

num_matched = 0
num_total = 0

val = {}

with open(in_path, "r") as data:
    with open(val_path, "r") as annotation:
        with open(data_path, "r") as text:
            with open(pos_path, "r") as pos:
                lines = data.readlines()
                annotations_val = annotation.readlines()
                sentences = text.readlines()
                postags = pos.readlines()

                for i in range(len(sentences)):
                    annotation_val = annotations_val[i]
                    sentence = sentences[i]
                    val[sentence] = annotation_val

                for i in range(0, len(lines), 2):
                    sent = lines[i]
                    postag = postags[i+1].split(" ")
                    vec = convert2vector(lines[i+1])
                    vec_val = convert2vector(val[sent])

                    if len(vec) == len(vec_val):
                        for j in range(len(vec)):
                            if postag[j] in ["NN", "NNS", "DT", "VB",
                                             "VBD", "VBN", "VBG", "VBP",
                                             "VBZ", "DT", "CD", "JJ", "RB",
                                             "RBR", 'RBS']:
                                num_total += 1
                                if vec[j] == vec_val[j]:
                                    num_matched += 1

print("Number of tokens: ", num_total)
print("Number of correct tokens: ", num_matched)
print("Percentage: ", (num_matched)/num_total)
