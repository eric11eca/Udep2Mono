import numpy as np
from tqdm import tqdm
from copy import deepcopy
from binarization import Binarizer
from dependency_parse import dependencyParse
from util import det_type, det_mark, negtive_implicative
from util import heapq, arrows, negate_mark, btreeToList, convert2vector


class Polarizer:
    def __init__(self, dependtree=None, relation=None):
        self.dependtree = dependtree
        self.sentence_head = []
        self.relation = relation
        self.polarize_function = {
            "acl:relcl": self.polarize_acl_relcl,
            "acl": self.polarize_acl_relcl,
            "advcl": self.polarize_acl_relcl,
            "nsubj": self.polarize_nsubj,
            "csubj": self.polarize_nsubj,
            "nsubj:pass": self.polarize_nsubj,
            "expl": self.polarize_expl,
            "dep": self.polarize_dep,
            "det": self.polarize_det,
            "det:predet": self.polarize_det,
            "obj": self.polarize_obj,
            "iobj": self.polarize_inherite,
            "case": self.polarize_case,
            "obl": self.polarize_inherite,
            "amod": self.polarize_amod,
            "conj": self.polarize_conj,
            "cc": self.polarize_cc,
            "advmod": self.polarize_advmod,
            "aux": self.polarize_inherite,
            "aux:pass": self.polarize_inherite,
            "obl:npmod": self.polarize_oblnpmod,
            "obl:tmod": self.polarize_inherite,
            "nummod": self.polarize_nummod,
            "cop": self.polarize_inherite,
            "xcomp": self.polarize_obj,
            "mark": self.polarize_inherite,
            "nmod": self.polarize_nmod,
            "compound": self.polarize_inherite,
            "compound:prt": self.polarize_inherite,
            "ccomp": self.polarize_ccomp,
            "nmod:poss": self.polarize_nsubj,
            "fixed": self.polarize_inherite,
            "goeswith": self.polarize_inherite,
            "parataxis": self.polarize_inherite,
            "appos": self.polarize_inherite,
        }
        self.treeLog = []
        self.polarLog = []

    def polarize_deptree(self):
        self.polarize(self.dependtree)

    def polarize(self, tree):
        if tree.isTree():
            self.polarize_function[tree.val](tree)

    def polarize_expl(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = "+"
        right.mark = "+"

        if self.sentence_head[-1].left.mark == "-":
            right.mark = "-"

    def polarize_acl_relcl(self, tree):
        self.polarLog.append("polarize_acl:relcl")
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
            left.mark = tree.mark
        else:
            tree.mark = "+"
            right.mark = "+"
            left.mark = "+"

        if right.isTree():
            self.polarize(right)

        tree.mark = right.mark
        if left.isTree():
            self.polarize(left)

        if right.mark == "-":
            self.negate(left, -1)
        elif right.mark == "=":
            self.equalize(left)

    def polarize_nsubj(self, tree):
        self.polarLog.append("polarize_nsubj")
        self.sentence_head.append(tree)
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
            left.mark = tree.mark
        else:
            tree.mark = "+"
            right.mark = "+"
            left.mark = "+"

        if self.searchDependency("expl", right):
            self.polarize(left)
            self.polarize(right)
            return

        self.polarize(right)

        if left.val.lower() == "that":
            self.equalize(right)

        if left.isTree():
            self.polarize(left)
        else:
            if left.val.lower() in ["nobody"]:
                self.negate(tree, self.relation.index(tree.key))

        if tree.mark == "0":
            tree.mark = right.mark

        if left.npos == "NN":
            left.mark = tree.mark

        self.sentence_head.pop()

    def polarize_dep(self, tree):
        self.polarLog.append("polarize_dep")

        right = tree.getRight()
        left = tree.getLeft()

        left.mark = "+"
        right.mark = "+"

        if right.isTree():
            self.polarize(right)

        if left.isTree():
            self.polarize(left)

    def polarize_obj(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
            left.mark = tree.mark
        else:
            right.mark = "+"
            left.mark = "+"

        # if self.sentence_head[-1].left.npos == "PRP":
        #    right.mark = "="

        if right.isTree():
            self.polarize(right)

        if left.isTree():
            self.polarize(left)

        if right.val.lower() in negtive_implicative:
            self.negate(left, -1)

        tree.mark = left.mark

    def polarize_obl(self, tree):
        self.polarLog.append("polarize_obl")

        right = tree.getRight()
        left = tree.getLeft()

        left.mark = tree.mark
        if left.isTree():
            self.polarize(left)

        right.mark = tree.mark
        if right.isTree():
            self.polarize(right)

    def searchDependency(self, deprel, tree):
        if tree.val == deprel:
            return True
        else:
            right = tree.getRight()
            left = tree.getLeft()

            leftFound = False
            rightFound = False

            if not isinstance(right, str) and right.isTree():
                rightFound = self.searchDependency(deprel, right)

            if not isinstance(left, str) and left.isTree():
                leftFound = self.searchDependency(deprel, left)

            return leftFound or rightFound

    def polarize_det(self, tree):
        self.polarLog.append("polarize_det")
        right = tree.getRight()
        left = tree.getLeft()

        detType = det_type(left.val)
        detMark = det_mark[detType]

        if tree.mark != "0":
            left.mark = tree.mark
        else:
            left.mark = detMark[0]

        right.mark = detMark[1]
        tree.mark = detMark[1]

        if right.isTree():
            self.polarize(right)

        if detType == "det:negation":
            self.negate(tree.parent, self.relation.index(tree.key))

    def polarize_inherite(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
            left.mark = tree.mark
        else:
            right.mark = "+"
            left.mark = "+"

        if right.isTree():
            self.polarize(right)

        if left.val.lower() == "there":
            left.mark = "+"
        if left.isTree():
            self.polarize(left)

    def polarize_conj(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if left.val == "det":
            self.polarize(left)
            tree.mark = left.mark
            right.mark = left.mark
            self.polarize(right)
        elif right.val == "det":
            self.polarize(right)
            tree.mark = right.mark
            left.mark = right.mark
            self.polarize(left)
        else:
            self.polarize_inherite(tree)

    def polarize_cc(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = "+"
        right.mark = tree.mark
        if right.isTree():
            self.polarize(right)

    def polarize_nmod_poss(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = tree.mark
        if left.isTree():
            self.polarize(left)
        else:
            left.mark = "+"

        right.mark = tree.mark
        if right.isTree():
            self.polarize(right)
        else:
            left.mark = "+"

    def polarize_amod(self, tree):
        left = tree.getLeft()
        right = tree.getRight()
        if left.val.lower() in ["many", "most"]:
            left.mark = "+"
            right.mark = "="
            if right.isTree():
                self.polarize(right)
        else:
            self.polarize_inherite(tree)

    def polarize_advmod(self, tree):
        left = tree.getLeft()
        right = tree.getRight()

        if left.val.lower() in ["many", "most"]:
            left.mark = "+"
            right.mark = "="
            if right.isTree():
                self.polarize(right)
        elif left.val.lower() in ["not", "no", "n’t"]:
            left.mark = "+"
            right.mark = tree.mark
            if right.isTree():
                self.polarize(right)
            self.negate(tree, self.relation.index(left.key))
            if tree.parent.val == "aux":
                tree.parent.left.mark = negate_mark[tree.parent.left.mark]
        else:
            self.polarize_inherite(tree)

    def polarize_case(self, tree):
        self.polarLog.append("polarize_case")

        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            left.mark = tree.mark
            right.mark = tree.mark
        else:
            left.mark = "+"
            right.mark = "+"

        if right.val == "least":
            tree.mark = "-"
            right.mark = "+"
            left.mark = right.mark
        elif right.val == "most":
            tree.mark = "+"
            right.mark = "+"
            left.mark = right.mark
            self.negate(self.sentence_head[-1], self.relation.index(tree.key))
        elif left.val == "without":
            if right.isTree():
                self.polarize(right)
            self.negate(tree, self.relation.index(left.key))
        elif right.npos == "CD":
            right.mark = "="
            if left.isTree():
                self.polarize(left)
        elif right.val == "nmod:poss":
            left.mark = "="
            if right.isTree():
                self.polarize(right)
        else:
            if right.isTree():
                self.polarize(right)
                tree.mark = right.mark
            if left.isTree():
                self.polarize(left)

    def polarize_oblnpmod(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if left.isTree():
            self.polarize(left)
        right.mark = left.mark
        if right.isTree():
            self.polarize(right)

    def polarize_nummod(self, tree):
        self.polarLog.append("polarize_nummod")
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = "-"
        right.mark = "+"

        if left.val.lower() in ["one", "1"]:
            left.mark = "="

        if tree.parent == "compound":
            right.mark = left.mark

        if right.isTree():
            self.polarize(right)

        if left.isTree():
            self.polarize(left)
        elif left.id == 1:
            left.mark = "="

    def polarize_nmod(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            left.mark = tree.mark
            right.mark = tree.mark
        else:
            left.mark = "+"
            right.mark = "+"

        if right.isTree():
            self.polarize(right)

        if right.npos == "DT":
            detType = det_type(right.val)
            left.mark = det_mark[detType][1]
        elif right.val.lower() in ["many", "most"]:
            left.mark = "="
        elif right.val.lower() in ["none"]:
            left.mark = "-"

        if left.isTree():
            self.polarize(left)

        tree.mark = right.mark
        if right.mark == "-":
            self.negate(left, -1)
        elif right.mark == "=":
            self.equalize(left)

    def polarize_ccomp(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark

        if right.isTree():
            self.polarize(right)

        left.mark = right.mark
        if left.isTree():
            self.polarize(left)

        # tree.mark = right.mark

    def equalize(self, tree):
        if tree.isTree():
            if tree.val != "nummod":
                self.equalize(tree.getRight())
                self.equalize(tree.getLeft())
                if tree.mark != "0":
                    tree.mark = "="
        else:
            if tree.npos != "CC":
                tree.mark = "="

    def negate_condition(self, tree, anchor):
        not_truch_connection = not tree.val in ["and", "or"]
        not_empty_mark = tree.mark != "0"
        return not_empty_mark and not_truch_connection

    def negate(self, tree, anchor):
        if tree.isTree():
            # print(tree.val)
            if self.relation.index(tree.key) > anchor or "nsubj" in tree.val:
                # print(tree.val)
                self.negate(tree.getRight(), anchor)
                self.negate(tree.getLeft(), anchor)
                if self.negate_condition(tree, anchor):
                    tree.mark = negate_mark[tree.mark]
        else:
            if self.relation.index(tree.key) > anchor and self.negate_condition(
                tree, anchor
            ):
                if tree.npos != "EX":
                    tree.mark = negate_mark[tree.mark]


def run_polarize_pipeline(sentences, annotations_val=[], verbose=0):
    binarizer = Binarizer()
    polarizer = Polarizer()

    annotations = []
    incorrect = []
    exceptioned = []
    num_unmatched = 0

    for i in tqdm(range(len(sentences))):
        # Universal Dependency Parse
        sent = sentences[i]
        if len(sent) == 0:
            return
        tree, postag, words = dependencyParse(sent)
        parseTreeCopy = deepcopy(tree)

        # Binarization
        binarizer.parseTable = parseTreeCopy
        binarizer.postag = postag
        binarizer.words = words
        sexpression = ""
        annotated = ""

        try:
            binaryDepdency, relation = binarizer.binarization()

            if verbose == 2:
                sexpression, annotated = btreeToList(
                    binaryDepdency, len(words), 0)
                sexpression = str(sexpression).replace(
                    ",", " ").replace("'", "")
        except Exception as e:
            if verbose == 2:
                print(str(e))
            exceptioned.append((sent, annotations_val[i]))
            continue

        # Polarization
        polarizer.dependtree = binaryDepdency
        polarizer.relation = relation
        try:
            polarizer.polarize_deptree()
        except Exception as e:
            if verbose == 2:
                print(str(e))
            exceptioned.append((sent, annotations_val[i]))
            continue

        # Postprocessing
        polarized, annotated = btreeToList(binaryDepdency, len(words), 0)
        polarized = str(polarized).replace(",", " ").replace("'", "")

        result = []
        while annotated:
            next_item = heapq.heappop(annotated)
            result.append(next_item[1])

        result = (
            str(result)
            .replace(",", " ")
            .replace("'", "")
            .replace("[", "")
            .replace("]", "")
        )

        vec = convert2vector(result)
        if len(annotations_val) > 0:
            annotation_val = annotations_val[i]
            vec_val = convert2vector(annotation_val)
            if len(vec) == len(vec_val):
                if np.prod(vec_val) != -1:
                    differece = np.sum(np.subtract(vec, vec_val))
                    if differece != 0:
                        num_unmatched += 1
                        one = not "1" in annotation_val
                        two = not "2" in annotation_val
                        three = not "3" in annotation_val
                        four = not "4" in annotation_val
                        five = not "5" in annotation_val
                        One = not "one" in annotation_val.lower()
                        if one and two and three and four and five and One:
                            incorrect.append(
                                (sent, result, annotation_val,
                                 np.array2string(
                                     np.array(vec), precision=2, separator=','),
                                 np.array2string(
                                     np.array(vec_val), precision=2, separator=',')))
                            continue

        # if verbose == 3:
        # print(polarizer.polarLog)

        annotations.append(
            {
                "annotated": result,
                "polarized": polarized,
                "sexpression": sexpression,
            }
        )
    print()
    print("Number of unmatched sentences: ", num_unmatched)
    return annotations, exceptioned, incorrect
