import numpy as np
from tqdm import tqdm
from copy import deepcopy
from binarization import Binarizer, BinaryDependencyTree
from dependency_parse import dependencyParse
from util import *
from util import heapq, arrows, negate_mark, btreeToList, convert2vector


class Polarizer:
    def __init__(self, dependtree=None, relation=None):
        self.dependtree = dependtree
        self.sentence_head = []
        self.relation = relation
        self.polarize_function = {
            "acl": self.polarize_acl_relcl,
            "acl:relcl": self.polarize_acl_relcl,
            "advcl": self.polarize_acl_relcl,
            "advmod": self.polarize_advmod,
            "advmod:count": self.polarize_advmod,
            "amod": self.polarize_amod,
            "appos": self.polarize_inherite,
            "aux": self.polarize_aux,
            "aux:pass": self.polarize_aux,
            "case": self.polarize_case,
            "cc": self.polarize_cc,
            "cc:preconj": self.polarize_det,
            "ccomp": self.polarize_ccomp,
            "compound": self.polarize_inherite,
            "compound:prt": self.polarize_inherite,
            "conj": self.polarize_inherite,
            "cop": self.polarize_inherite,
            "csubj": self.polarize_nsubj,
            "csubj:pass": self.polarize_nsubj,
            "dep": self.polarize_dep,
            "det": self.polarize_det,
            "det:predet": self.polarize_det,
            "discourse": self.polarize_inherite,
            "expl": self.polarize_expl,
            "fixed": self.polarize_inherite,
            "flat": self.polarize_inherite,
            "goeswith": self.polarize_inherite,
            "iobj": self.polarize_inherite,
            "mark": self.polarize_inherite,
            "nmod": self.polarize_nmod,
            "nmod:npmod": self.polarize_nmod,
            "nmod:tmod": self.polarize_nmod,
            "nmod:poss": self.polarize_nmod_poss,
            "nsubj": self.polarize_nsubj,
            "nsubj:pass": self.polarize_nsubj,
            "nummod": self.polarize_nummod,
            "obj": self.polarize_obj,
            "obl": self.polarize_obj,
            "obl:npmod": self.polarize_oblnpmod,
            "obl:tmod": self.polarize_inherite,
            "parataxis": self.polarize_inherite,
            "xcomp": self.polarize_obj,
        }
        self.treeLog = []
        self.polarLog = []

    def polarize_deptree(self):
        self.polarize(self.dependtree)

    def polarize(self, tree):
        if tree.isTree():
            self.polarize_function[tree.val](tree)

    def polarize_acl_relcl(self, tree):
        self.polarLog.append("polarize_acl:relcl")
        self.sentence_head.append(tree)
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
        else:
            tree.mark = "+"
            right.mark = "+"

        left.mark = "+"
        if left.isTree():
            self.polarize(left)
        if right.isTree():
            self.polarize(right)

        tree.mark = right.mark

        if right.mark == "-" and left.npos != "VBD":
            self.negate(left, -1)
        elif right.mark == "=" and left.npos != "VBD":
            self.equalize(left)
        elif right.val == "impossible":
            self.negate(left, -1)

        self.sentence_head.pop()

    def polarize_advmod(self, tree):
        left = tree.getLeft()
        right = tree.getRight()

        self.polarize_inherite(tree)

        more_than = False
        less_than = False

        if tree.left.val == "fixed":
            more_than = tree.left.right.val.lower(
            ) == "more" and tree.left.left.val.lower() == "than"
            less_than = tree.left.right.val.lower(
            ) == "less" and tree.left.left.val.lower() == "than"

        if left.val.lower() in ["many", "most"]:
            right.mark = "="
            if isinstance(tree.parent, BinaryDependencyTree) and tree.parent.val == "amod":
                self.equalize(tree.parent.right)
        elif left.val.lower() in ["not", "no", "n’t", "never"]:
            self.negate(right, self.relation.index(left.key))
        elif left.val.lower() in ["exactly"]:
            self.equalize(right)
            tree.mark = right.mark
        elif more_than:
            if right.val == "nummod":
                right.left.mark = "-"
        elif less_than:
            self.negate(right, self.relation.index(tree.key))
            if right.val == "nummod":
                right.left.mark = "+"

        if left.val.lower() == "when":
            self.equalize(self.dependtree)

    def polarize_amod(self, tree):
        left = tree.getLeft()
        right = tree.getRight()
        self.polarize_inherite(tree)

        at_most = False
        at_least = False

        if isinstance(tree.parent, BinaryDependencyTree):
            at_most = tree.parent.left.val.lower() == "at" and left.val.lower() == "most"
            at_least = tree.parent.left.val.lower() == "at" and left.val.lower() == "least"

        if at_most:
            self.negate(right, self.relation.index(tree.key))
            if right.val == "nummod":
                right.left.mark = "+"
        elif at_least:
            if right.left.val == "nummod":
                right.left.mark = "-"
        elif left.val.lower() in ["many", "most"] and not at_most:
            right.mark = "="
            tree.mark = right.mark

    def polarize_aux(self, tree):
        self.polarize_inherite(tree)

    def polarize_case(self, tree):
        self.polarLog.append("polarize_case")

        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            left.mark = tree.mark
            right.mark = tree.mark
        else:
            tree.mark = "+"
            left.mark = "+"
            right.mark = "+"

        if right.val == "least":
            tree.mark = "-"
            right.mark = "+"
            left.mark = right.mark
        elif right.val == "most":
            self.top_down_negate(tree, "case", self.relation.index(tree.key))
        elif left.val == "without":
            if right.isTree():
                self.polarize(right)
            self.negate(tree, self.relation.index(left.key))
        elif right.npos == "CD":
            right.mark = "="
            if left.isTree():
                self.polarize(left)
        elif left.val.lower() == "for":
            if right.isTree():
                self.polarize(right)
            self.equalize(right)
        elif right.val == "nmod:poss":
            left.mark = "="
            if right.isTree():
                self.polarize(right)
        else:
            if left.isTree():
                self.polarize(left)
            if right.isTree():
                self.polarize(right)
                tree.mark = right.mark

    def polarize_cc(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = "+"
        right.mark = "+"

        if right.val != "expl" and right.val != "det":
            right.mark = tree.mark

        if right.isTree():
            self.polarize(right)

        if left.id == 1:
            self.equalize(right)

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

    def polarize_dep(self, tree):
        self.polarLog.append("polarize_dep")

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

        if left.isTree():
            self.polarize(left)

    def polarize_det(self, tree):
        self.polarLog.append("polarize_det")
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            left.mark = tree.mark
            right.mark = tree.mark
        else:
            left.mark = "+"
            right.mark = "+"

        detType = det_type(left.val)
        if detType is None:
            detType = "det:exist"
        detMark = det_mark[detType]

        right.mark = detMark[1]
        tree.mark = detMark[1]

        if right.isTree():
            self.polarize(right)

        if detType == "det:negation":
            self.top_down_negate(tree, "det", self.relation.index(tree.key))

    def polarize_expl(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = "+"
        right.mark = "+"

        if self.dependtree.left.mark == "-":
            right.mark = "-"

        if left.isTree():
            self.polarize(left)

        if right.isTree():
            self.polarize(right)

    def polarize_nmod(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
        else:
            right.mark = "+"
        left.mark = "+"

        if right.npos == "DT" or right.npos == "CC":
            detType = det_type(right.val)
            if detType == None:
                detType = "det:exist"
            left.mark = det_mark[detType][1]
            if detType == "det:negation":
                self.top_down_negate(
                    tree, "nmod", self.relation.index(tree.key))
        elif right.val.lower() in ["many", "most"]:
            left.mark = "="

        if left.isTree():
            self.polarize(left)

        if right.isTree():
            self.polarize(right)

        tree.mark = right.mark
        if right.mark == "-":
            self.negate(left, -1)
        elif right.mark == "=":
            self.equalize(left)

    def polarize_nmod_poss(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = tree.mark
        if left.isTree():
            self.polarize(left)
        else:
            left.mark = "+"

        right.mark = tree.mark
        if self.searchDependency("det", tree.left):
            right.mark = left.mark
        if right.isTree():
            self.polarize(right)
        else:
            right.mark = "+"

    def polarize_nsubj(self, tree):
        self.polarLog.append("polarize_nsubj")
        # self.sentence_head.append(tree)
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
        if not isinstance(tree.parent, str):
            if tree.parent.left.val.lower() == "that":
                self.equalize(left)

        if left.isTree():
            self.polarize(left)
        else:
            if left.val.lower() in ["nobody"]:
                self.negate(tree, self.relation.index(tree.key))

        if tree.mark == "0":
            tree.mark = right.mark

        if left.npos == "NN":
            left.mark = tree.mark

        if is_implicative(right.val.lower(), negtive_implicative):
            tree.mark = "-"

    def polarize_nummod(self, tree):
        self.polarLog.append("polarize_nummod")
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = "-"
        if tree.mark != "0":
            right.mark = tree.mark
        else:
            right.mark = "+"

        if left.val.lower() in ["one", "1"]:
            left.mark = "="

        if tree.parent == "compound":
            right.mark = left.mark

        if left.isTree():
            self.polarize(left)
            if left.mark == "=":
                right.mark = left.mark
                tree.mark = left.mark
        elif left.id == 1:
            left.mark = "="

        if not isinstance(tree.parent, str):
            if is_implicative(tree.parent.right.val, at_least_implicative):
                right.mark = "-"

        if right.isTree():
            self.polarize(right)

    def polarize_obj(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
        else:
            right.mark = "+"
            tree.mark = "+"
        left.mark = "+"

        if right.isTree():
            self.polarize(right)

        if left.isTree():
            self.polarize(left)

        if is_implicative(right.val.lower(), negtive_implicative):
            tree.mark = "-"
            self.negate(left, -1)

    def polarize_obl(self, tree):
        self.polarLog.append("polarize_obl")

        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
        else:
            right.mark = "+"
        left.mark = "+"

        if right.isTree():
            self.polarize(right)

        if left.isTree():
            self.polarize(left)

        if right.mark == "-":
            self.negate(left, -1)

    def polarize_oblnpmod(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if left.isTree():
            self.polarize(left)
        right.mark = left.mark
        if right.isTree():
            self.polarize(right)

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
        elif left.val.lower() == "if":
            self.negate(right, -1)

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

    def verbMarkReplace(self, tree, mark):
        if isinstance(tree, str):
            return
        if tree.npos is not None and "VB" in tree.npos:
            tree.mark = mark
        self.verbMarkReplace(tree.left, mark)
        self.verbMarkReplace(tree.right, mark)

    def equalize(self, tree):
        if tree.isTree():
            self.equalize(tree.getRight())
            self.equalize(tree.getLeft())
            if tree.mark != "0":
                tree.mark = "="
        else:
            if tree.npos != "CC" and tree.val.lower() != "when":
                tree.mark = "="

    def negate_condition(self, tree, anchor):
        not_truth_connection = not tree.val in ["and", "or"]
        not_empty_mark = tree.mark != "0"
        return not_empty_mark and not_truth_connection

    def top_down_negate(self, tree, deprel, anchor):
        if not isinstance(tree.parent, BinaryDependencyTree):
            return
        if tree.parent.left.val == deprel:
            self.negate(tree.parent.left, anchor)
            self.negate(tree.parent.right, -1)
        elif tree.parent.right.val == deprel:
            self.negate(tree.parent.right, anchor)
            self.negate(tree.parent.left, -1)

    def negate(self, tree, anchor):
        if isinstance(tree, str):
            return
        if tree.val == "cc" and tree.right.val in ["expl", "nsubj", "det"]:
            return
        if tree.isTree():
            # print(tree.val)
            if self.relation.index(tree.key) > anchor or "nsubj" in tree.val:
                # print(tree.val)
                self.negate(tree.getRight(), anchor)
                self.negate(tree.getLeft(), anchor)
                if self.negate_condition(tree, anchor):
                    tree.mark = negate_mark[tree.mark]
        else:
            if self.relation.index(tree.key) > anchor and self.negate_condition(tree, anchor):
                if tree.npos != "EX":
                    tree.mark = negate_mark[tree.mark]


def run_polarize_pipeline(sentences, annotations_val=[], verbose=0, parser="stanza"):
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
            continue

        tree, postag, words = dependencyParse(sent, parser=parser)
        parseTreeCopy = deepcopy(tree)

        # print("s")
        # print(words)
        # print(parseTreeCopy)

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
                sexpression = '[%s]' % ', '.join(
                    map(str, sexpression)).replace(",", " ")
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
            polarized, annotated = btreeToList(binaryDepdency, len(words), 0)
            polarized = '[%s]' % ', '.join(
                map(str, polarized)).replace("'", "")
            polarized = polarized.replace(",", "")
        except Exception as e:
            if verbose == 2:
                print(str(e))
            print(sent)
            exceptioned.append((sent, annotations_val[i]))
            continue

        # Postprocessing
        result = []
        while annotated:
            next_item = heapq.heappop(annotated)
            result.append(next_item[1])

        result = '%s' % ', '.join(map(str, result)).replace(",", "")

        vec = convert2vector(result)
        if len(annotations_val) > 0:
            annotation_val = annotations_val[i]
            vec_val = convert2vector(annotation_val)
            if len(vec) == len(vec_val):
                if np.prod(vec_val) != -1:
                    differece = np.sum(np.subtract(vec, vec_val))
                    if differece != 0:
                        num_unmatched += 1
                        #one = not "1" in annotation_val
                        #two = not "2" in annotation_val
                        #three = not "3" in annotation_val
                        #four = not "4" in annotation_val
                        #five = not "5" in annotation_val
                        #One = not "one" in annotation_val.lower()
                        # if one and two and three and four and five and One:
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
                # "validation": annotations_val[i]
            }
        )
    print()
    print("Number of unmatched sentences: ", num_unmatched)
    return annotations, exceptioned, incorrect
