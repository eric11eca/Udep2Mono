from copy import deepcopy
from util import heapq, arrows, negate_mark, btreeToList
from util import det_type, det_mark, negtive_implicative
from dependency_parse import dependencyParse
from binarization import Binarizer


class Polarizer:
    def __init__(self, dependtree, relation):
        self.dependtree = dependtree
        self.sentence_head = []
        self.relation = relation
        self.polarize_function = {
            "acl:relcl": self.polarize_acl_relcl,
            "nsubj": self.polarize_nsubj,
            "nsubj:pass": self.polarize_nsubj,
            "dep": self.polarize_dep,
            "det": self.polarize_det,
            "obj": self.polarize_obj,
            "case": self.polarize_case,
            "obl": self.polarize_obl,
            "amod": self.polarize_amod,
            "conj": self.polarize_inherite,
            "cc": self.polarize_cc,
            "advmod": self.polarize_advmod,
            "aux": self.polarize_inherite,
            "aux:pass": self.polarize_inherite,
            "obl:npmod": self.polarize_oblnpmod,
            "nummod": self.polarize_nummod,
            "cop": self.polarize_inherite,
            "xcomp": self.polarize_obj,
            "mark": self.polarize_inherite,
            "nmod": self.polarize_nmod,
            "compound": self.polarize_inherite,
            "ccomp": self.polarize_ccomp,
            "nmod:poss": self.polarize_nsubj,
            "fixed": self.polarize_inherite
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
        right = tree.getRight()
        left = tree.getLeft()

        if right.isTree():
            self.polarize(right)
        else:
            right.mark = "+"

        tree.mark = right.mark
        if left.isTree():
            self.polarize(left)

        if right.mark == "-":
            self.negate(left, -1)

    def polarize_nsubj(self, tree):
        self.polarLog.append("polarize_nsubj")

        self.sentence_head.append(tree)
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
            left.mark = tree.mark
        else:
            right.mark = '+'
            left.mark = '+'

        self.polarize(right)

        # print("polarize_left")

        if left.isTree():
            self.polarize(left)

        if tree.mark == "0":
            tree.mark = right.mark
        self.sentence_head.pop()

    def polarize_dep(self, tree):
        self.polarLog.append("polarize_dep")

        right = tree.getRight()
        left = tree.getLeft()

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
            right.mark = '+'
            left.mark = '+'

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
        else:
            left.mark = '+'

        right.mark = tree.mark
        if right.isTree():
            self.polarize(right)
        else:
            left.mark = '+'

    def polarize_det(self, tree):
        self.polarLog.append("polarize_det")

        right = tree.getRight()
        left = tree.getLeft()

        detType = det_type(left.val)
        detMark = det_mark[detType]

        if tree.mark != "0" and len(self.sentence_head) > 1:
            left.mark = tree.mark
        else:
            left.mark = detMark[0]

        right.mark = detMark[1]
        tree.mark = detMark[1]

        if right.isTree():
            self.polarize(right)

        if detType == "det:negation":
            self.negate(self.sentence_head[-1], self.relation.index(tree.key))

    def polarize_inherite(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        right.mark = tree.mark
        if right.isTree():
            self.polarize(right)

        left.mark = right.mark
        if left.isTree():
            self.polarize(left)

    def polarize_cc(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = '+'
        if right.isTree():
            self.polarize(right)
        else:
            right.mark = tree.mark

    def polarize_nmod_poss(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = tree.mark
        if left.isTree():
            self.polarize(left)
        else:
            left.mark = '+'

        right.mark = tree.mark
        if right.isTree():
            self.polarize(right)
        else:
            left.mark = '+'

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
        elif left.val.lower() in ["not", "no", "n't"]:
            left.mark = "+"
            right.mark = tree.mark
            if right.isTree():
                self.polarize(right)
            self.negate(self.sentence_head[-1], self.relation.index(left.key))
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
        # elif left.val == "in":
        #    right.mark = "-"
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

        if right.isTree():
            self.polarize(right)

        left.mark = right.mark
        if left.isTree():
            self.polarize(left)

        tree.mark = right.mark

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

        #tree.mark = right.mark

    def equalize(self, tree):
        if tree.isTree():
            if tree.val != "nummod":
                self.equalize(tree.getRight())
                self.equalize(tree.getLeft())
                if tree.mark != "0":
                    tree.mark = "="
        else:
            tree.mark = "="

    def negate(self, tree, anchor):
        if tree.isTree():
            # print(tree.val)
            if self.relation.index(tree.key) > anchor or "nsubj" in tree.val:
                # print(tree.val)
                self.negate(tree.getRight(), anchor)
                self.negate(tree.getLeft(), anchor)
                if anchor and tree.mark != "0":
                    tree.mark = negate_mark[tree.mark]
        else:
            if self.relation.index(tree.key) > anchor and tree.mark != "0":
                tree.mark = negate_mark[tree.mark]


def run_polarize_pipeline(sentences, annotations=[], verbose=0):
    binarizer = Binarizer()
    annotations = []

    for i in range(len(sentences)):
        # Universal Dependency Parse
        sent = sentences[i]
        tree, postag, words = dependencyParse(sent)
        parseTreeCopy = deepcopy(tree)

        # Binarization
        binarizer.parseTable = parseTreeCopy
        binarizer.postag = postag
        binarizer.words = words
        binaryDepdency, relation = binarizer.binarization()

        sexpression, annotated = btreeToList(binaryDepdency, len(words), 0)
        sexpression = str(sexpression).replace(',', ' ').replace("'", '')
        if verbose == 2:
            print(sexpression)

        # Polarization
        polarizer = Polarizer(binaryDepdency, relation)
        polarizer.polarize_deptree()

        # Postprocessing
        polarized, annotated = btreeToList(binaryDepdency, len(words), 0)
        polarized = str(polarized).replace(',', ' ').replace("'", '')
        if verbose == 2:
            print(polarized)

        result = []
        while annotated:
            next_item = heapq.heappop(annotated)
            result.append(next_item[1])

        result = str(result).replace(',', ' ').replace(
            "'", '').replace("[", "").replace("]", "")

        if verbose == 3:
            print(polarizer.treeLog)

        annotations.append({
            "annotated": result,
            "polarized": polarized,
            "sexpression": sexpression
        })

    return annotations
