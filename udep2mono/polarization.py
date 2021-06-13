import svgling
import numpy as np
from tqdm import tqdm
from copy import deepcopy
from binarization import Binarizer, BinaryDependencyTree
from dependency_parse import dependency_parse
from util import *


scalar_comparative = {
    "taller": ["+", "-"],
    "lower": ["-", "+"],
    "higher": ["-", "+"],
    "faster": ["+", "-"],
    "slower": ["-", "+"],
    "longer": ["+", "-"],
    "shorter": ["-", "+"],
    "heavier": ["+", "-"],
    "lighter": ["-", "+"],
    "deeper": ["+", "-"],
    "shawlloer": ["-", "+"],
    "brighter": ["+", "-"],
    "darker": ["-", "+"],
    "hotter": ["+", "-"],
    "colder": ["-", "+"],
    "warmer": ["+", "-"],
    "cooler": ["-", "+"],
    "bigger": ["+", "-"],
    "larger": ["+", "-"],
    "smaller": ["-", "+"],
    "more": ["+", "-"],
    "less": ["-", "+"],
    "fewer": ["-", "+"],
    "greater": ["+", "-"],
    "stronger": ["+", "-"],
    "weaker": ["-", "+"],
    "dryer": ["-", "+"],
    "wetter": ["+", "-"],
    "tigher": ["+", "-"],
    "loose": ["-", "+"],
    "farther": ["+", "-"],
    "closer": ["-", "+"],
}


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
            "aux": self.polarize_inherite,
            "aux:pass": self.polarize_inherite,
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
            "obl": self.polarize_obl,
            "obl:npmod": self.polarize_oblnpmod,
            "obl:tmod": self.polarize_obltmod,
            "parataxis": self.polarize_inherite,
            "xcomp": self.polarize_obj,
        }
        self.tree_log = []
        self.polar_log = []

        self.DETEXIST = "det:exist"
        self.DETNEGATE = "det:negation"

        self.nsubj_right_equal = False

    def polarize_deptree(self):
        self.polarize(self.dependtree)

    def polarize(self, tree):
        if tree.is_tree:
            self.polarize_function[tree.val](tree)

    def polarize_acl_relcl(self, tree):
        self.sentence_head.append(tree)
        self.right_inheritance(tree)
        right = tree.right
        left = tree.left

        verb = self.down_right(tree)
        original_verbState = tree.counter.willing_verb
        if(verb.val.lower() in willing_verbs and left.val == "mark" and left.left.val.lower() == "to"):
            tree.counter.willing_verb = True

        if left.is_tree:
            self.polarize(left)

        tree.counter.willing_verb = original_verbState

        if right.is_tree:
            self.polarize(right)

        if right.id == 1:
            right.mark = "-"

        tree.mark = right.mark

        if right.mark == "-" and left.pos != "VBD":
            self.negate(left, -1)
        elif right.mark == "=" and left.pos != "VBD":
            self.equalize(left)
        elif right.val == "impossible":
            self.negate(left, -1)

        self.sentence_head.pop()

    def polarize_advmod(self, tree):
        left = tree.left
        right = tree.right
        self.polarize_inherite(tree)
        root_mark = tree.mark

        if left.val.lower() in ["many", "most"]:
            right.mark = "="
            if isinstance(tree.parent, BinaryDependencyTree) and tree.parent.val == "amod":
                self.equalize(tree.parent.right)
        elif left.val.lower() in ["not", "no", "n't", "never", "rarely", "barely", "seldom", "only", "hardly", "infrequently", "unfrequently"]:
            self.negate(right, -1)
        elif left.val.lower() in ["exactly"]:
            self.equalize(tree.parent.parent)
            left.mark = root_mark
            tree.mark = right.mark

        if left.val.lower() == "when":
            self.equalize(self.dependtree)

    def polarize_amod(self, tree):
        left = tree.left
        right = tree.right
        self.polarize_inherite(tree)

        if left.val.lower() in ["many", "most"]:
            self.equalize(right)
            tree.mark = right.mark
        elif left.val.lower() in ["few", "no-longer"]:
            self.top_down_negate(
                tree, "amod", self.relation.index(tree.key))
            right.mark = "-"
            self.polarize(right)
        elif self.down_left(tree).val.lower() in ["fewer", "less"]:
            self.noun_mark_replace(right, "-")
            left.mark = "+"
            if(tree.parent.val == "acl:relcl"):
                self.equalize(tree.parent.left)
        elif self.down_left(tree).val.lower() in ["more"]:
            if(tree.parent.val == "acl:relcl"):
                self.equalize(tree.parent.left)
        elif left.val == "advmod":
            if left.right.val == "many":
                self.equalize(right)
                tree.mark = right.mark
            if left.left.val.lower() == "not":
                self.top_down_negate(
                    tree, "amod", self.relation.index(tree.key))
        elif left.val == "out-of":
            if(tree.parent is not None and tree.parent.val == "nummod" and right.val == "nummod"):
                left.mark = "-"
                right.mark = "--"
            self.polarize(right)

    def polarize_case(self, tree):
        self.polarize_inherite(tree)
        right = tree.right
        left = tree.left

        if left.val == "without":
            if right.is_tree:
                self.polarize(right)
            self.negate(tree.left, -1)
        elif right.pos == "CD":
            right.mark = "="
            if left.is_tree:
                self.polarize(left)
        elif right.val == "nmod:poss":
            left.mark = "="
            if right.is_tree:
                self.polarize(right)
        elif left.val == "except":
            right.mark = "="
            if right.is_tree and right.left.val == "for":
                self.nsubj_right_equal = True

        # duration case "for"
        elif left.val.lower() == "for" and right.val == "nummod":
            right.mark = "-"
            self.polarize(right)
        elif left.val == "than":
            temp, changes = self.find_comparative(tree)
            if(temp is not None and changes is not None):
                if(changes[0] != "+"):
                    temp.parent.mark = changes[0]
                    self.polarize(temp.parent)

                if(changes[1] != "+"):
                    right.mark = changes[1]
                    self.polarize(right)

    def polarize_cc(self, tree):
        self.full_inheritance(tree)
        right = tree.right
        left = tree.left

        if right.val != "expl" and right.val != "det":
            right.mark = tree.mark

        if right.is_tree:
            self.polarize(right)

        if left.val == "but":
            right.mark = negate_mark[tree.mark]
            tree.mark = negate_mark[tree.mark]

        if left.id == 1:
            self.equalize(right)

    def polarize_ccomp(self, tree):
        right = tree.right
        left = tree.left

        if tree.mark != "0":
            right.mark = tree.mark

        if right.is_tree:
            self.polarize(right)

        left.mark = right.mark
        if left.is_tree:
            self.polarize(left)

    def polarize_dep(self, tree):
        self.full_inheritance(tree)
        right = tree.right
        left = tree.left

        if right.is_tree:
            self.polarize(right)

        if left.is_tree:
            self.polarize(left)

    def polarize_det(self, tree):
        self.full_inheritance(tree)
        right = tree.right
        left = tree.left

        if(tree.counter.willing_verb):
            tree.mark = "="
            left.mark = "="
            self.polarize(left)
            right.mark = "="
            self.polarize(right)
            return

        dettype = det_type(left.val)
        if dettype is None:
            dettype = self.DETEXIST

        if left.val.lower() == "any":
            has_roots = isinstance(tree.parent, BinaryDependencyTree)
            has_roots = has_roots and isinstance(
                tree.parent.parent, BinaryDependencyTree)
            if has_roots:
                negate_signal = tree.parent.parent.left
                if negate_signal.val == "not":
                    dettype = self.DETEXIST
                if negate_signal.val == "det" and negate_signal.left.val.lower() == "no":
                    dettype = self.DETEXIST
                if tree.counter.addi_negates % 2 == 1:
                    dettype = self.DETEXIST

        detmark = det_mark[dettype]
        right.mark = detmark
        tree.mark = detmark

        det = str((left.val, left.id))
        at_least = self.replaced.get(det, "det").lower() in [
            "at-least", "more-than"]
        at_most = self.replaced.get(det, "det").lower() in [
            "at-most", "less-than"]

        if right.is_tree:
            if right.val == "nummod":
                right.mark = [detmark]
            self.polarize(right)
            if right.val == "nummod":
                if at_least:
                    right.left.mark = "-"
                elif at_most:
                    right.left.mark = "+"
        elif right.pos == 'CD':
            if at_least:
                right.mark = "-"
            elif at_most:
                right.mark = "+"

        if dettype == self.DETNEGATE:
            self.top_down_negate(tree, "det", self.relation.index(tree.key))

        if "not-" in self.replaced.get(det, "det").lower() and len(self.replaced.get(det, "det").lower().split('-')) == 2:
            self.negate(tree.parent, -1)

    def polarize_expl(self, tree):
        self.full_inheritance(tree)
        right = tree.right
        left = tree.left

        if self.dependtree.left.mark == "-":
            right.mark = "-"

        if left.is_tree:
            self.polarize(left)

        if right.is_tree:
            self.polarize(right)

    def polarize_nmod(self, tree):
        self.right_inheritance(tree)
        right = tree.right
        left = tree.left

        if right.pos == "DT" or right.pos == "CC":
            detType = det_type(right.val)
            if detType == None:
                detType = self.DETEXIST
            left.mark = det_mark[detType]
            if detType == "det:negation":
                self.top_down_negate(
                    tree, "nmod", self.relation.index(tree.key))
        elif right.val.lower() in ["many", "most"]:
            left.mark = "="

        if left.is_tree:
            self.polarize(left)

        if right.is_tree:
            self.polarize(right)

        if left.val == "case":
            if isinstance(tree.parent, BinaryDependencyTree):
                if tree.parent.left.val.lower() == "more":
                    left.right.mark = "-"

        tree.mark = right.mark
        if right.mark == "-":
            if(self.down_left(left).val != "than"):
                self.negate(left, -1)
        elif right.mark == "=":
            if right.left.val != "the":
                self.equalize(left)
            elif right.left.mark == "-":
                self.negate(left, -1)

    def polarize_nmod_poss(self, tree):
        right = tree.right
        left = tree.left

        left.mark = tree.mark
        if left.is_tree:
            self.polarize(left)
        else:
            left.mark = "+"

        right.mark = tree.mark
        if self.search_dependency("det", tree.left):
            right.mark = left.mark
        if right.is_tree:
            self.polarize(right)
        else:
            right.mark = "+"

    def polarize_nsubj(self, tree):
        self.full_inheritance(tree)
        right = tree.right
        left = tree.left

        if self.search_dependency("expl", right):
            self.polarize(left)
            self.polarize(right)
            return

        # increment counter
        if(((left.val == "det" or left.val == "amod") and left.left.val.lower() in det_type_words["det:negation"])
                or (right.val == "advmod" and right.left.val in ["not", "n't"])):
            tree.counter.add_negates()
        if((left.val == "det" and left.val.lower() in det_type_words["det:univ"])):
            tree.counter.add_unifies()

        self.polarize(right)
        tree.counter.nsubjLeft = True

        # if left.val.lower() == "that":
        #    self.equalize(right)
        # if not tree.is_root:
        #    if tree.parent.left.val.lower() == "that":
        #        self.equalize(left)

        if left.is_tree:
            self.polarize(left)
        else:
            if left.val.lower() in ["nobody"]:
                self.negate(tree, self.relation.index(tree.key))

        if tree.mark == "0":
            tree.mark = right.mark

        if left.pos == "NN":
            left.mark = tree.mark

        if is_implicative(right.val.lower(), "-"):
            tree.mark = "-"

        if self.nsubj_right_equal:
            self.equalize(right)

    def polarize_nummod(self, tree):
        right = tree.right
        left = tree.left

        left.mark = "="
        if tree.mark != "0":
            right.mark = "="
            if tree.mark == "-":
                left.mark = "-"
                right.mark = "-"
            elif type(tree.mark) is list:
                right.mark = tree.mark[0]
                tree.mark = right.mark
            elif tree.mark == "--":
                left.mark = "-"
                tree.mark = "+"
        else:
            right.mark = "="
        if left.val == "det":
            left.mark = "+"

        if tree.parent == "compound":
            right.mark = left.mark

        if left.is_tree:
            if left.val == "advmod":
                left.mark = "+"
            self.polarize(left)
            if left.mark == "=":
                right.mark = left.mark
                tree.mark = left.mark
        elif left.id == 1:
            left.mark = "="

        if not tree.is_tree:
            if is_implicative(tree.parent.right.val, "-"):
                left.mark = "-"
            elif is_implicative(tree.parent.right.val, "="):
                left.mark = "="

        if(tree.counter.willing_verb):
            left.mark = "="
            right.mark = "="
            tree.mark = "="

        if right.is_tree:
            self.polarize(right)

    def polarize_obj(self, tree):
        self.right_inheritance(tree)
        right = tree.right
        left = tree.left

        if right.is_tree:
            self.polarize(right)

        if left.is_tree:
            self.polarize(left)

        tree.mark = left.mark

        if is_implicative(right.val.lower(), "-"):
            tree.mark = "-"
            self.negate(left, -1)

        if left.val == "mark" and left.left.val == "to":
            left.left.mark = right.mark

    def polarize_obl(self, tree):
        self.right_inheritance(tree)
        right = tree.right
        left = tree.left

        scalar_arrow = "+"
        if right.is_tree:
            self.polarize(right)
            try:
                scalar_arrow = scalar_comparative[right.left.val][1]
            except KeyError:
                pass
        else:
            try:
                scalar_arrow = scalar_comparative[right.val][1]
            except KeyError:
                pass

        if left.is_tree:
            self.polarize(left)
            if left.right.val == "nummod":
                left.right.left.mark = scalar_arrow
            elif left.right.pos == "CD":
                left.right.mark = scalar_arrow
            tree.mark = left.mark

        if right.mark == "-":
            self.negate(left, -1)

    def polarize_obltmod(self, tree):
        right = tree.right
        left = tree.left

        if left.is_tree:
            self.polarize(left)

        if right.is_tree:
            self.polarize(right)

    def polarize_oblnpmod(self, tree):
        right = tree.right
        left = tree.left

        if left.is_tree:
            self.polarize(left)
        right.mark = left.mark
        if right.is_tree:
            self.polarize(right)

    def polarize_inherite(self, tree):
        self.full_inheritance(tree)
        right = tree.right
        left = tree.left

        if right.is_tree:
            self.polarize(right)

        if left.val.lower() == "there":
            left.mark = "+"

        if left.is_tree:
            self.polarize(left)
        elif left.val.lower() == "if":
            if(not(tree.parent != None and self.down_right(tree.parent).val in if_verbs)):
                self.negate(right, -1)

    def search_dependency(self, deprel, tree):
        if tree.val == deprel:
            return True
        else:
            right = tree.right
            left = tree.left

            left_found = False
            right_found = False

            if right is not None and right.is_tree:
                right_found = self.search_dependency(deprel, right)

            if left is not None and left.is_tree:
                left_found = self.search_dependency(deprel, left)

            return left_found or right_found

    def down_left(self, tree):
        if(tree.left == None):
            return tree
        return self.down_left(tree.left)

    def down_right(self, tree):
        if(tree.right == None):
            return tree
        return self.down_right(tree.right)

    def find_comparative(self, tree):
        parent = tree.parent
        modified, comp = self.find_right(parent, "amod")
        if(modified is None):
            return None, None
        return modified, scalar_comparative[comp.val.lower()]

    def find_right(self, tree, val):
        if(tree.right is None):
            return None, None
        if(tree.val == val):
            comp = self.down_left(tree)
            if comp.val.lower() in scalar_comparative:
                return tree, comp
            return self.find_right(tree.right, val)
        return self.find_right(tree.right, val)

    def find_comp_modifying(self, tree):
        if(tree.val == "amod"):
            return tree.right
        if(tree.is_root):
            return None
        return self.find_comp_modifying(tree.parent)

    def noun_mark_replace(self, tree, mark):
        if isinstance(tree, str):
            return False
        if tree.pos is not None and "NN" in tree.pos:
            tree.mark = mark
            return True
        right = self.noun_mark_replace(tree.right, mark)
        if not right:
            self.noun_mark_replace(tree.left, mark)

    def right_inheritance(self, tree):
        if tree.mark != "0":
            tree.right.mark = tree.mark
        else:
            tree.right.mark = "+"
            tree.mark = "+"
        tree.left.mark = "+"

    def full_inheritance(self, tree):
        if tree.mark != "0":
            tree.right.mark = tree.mark
            tree.left.mark = tree.mark
        else:
            tree.right.mark = "+"
            tree.left.mark = "+"
            tree.mark = "+"

    def equalize(self, tree):
        if tree.is_tree:
            self.equalize(tree.right)
            self.equalize(tree.left)
            if tree.mark != "0":
                tree.mark = "="
        else:
            if tree.pos != "CC" and tree.val.lower() != "when":
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
        if tree.is_tree:
            # print(tree.val)
            if self.relation.index(tree.key) > anchor or "nsubj" in tree.val:
                # print(tree.val)
                self.negate(tree.right, anchor)
                self.negate(tree.left, anchor)
                if self.negate_condition(tree, anchor):
                    tree.mark = negate_mark[tree.mark]
        else:
            if self.relation.index(tree.key) > anchor and self.negate_condition(tree, anchor):
                if tree.pos != "EX":
                    # print(tree.val)
                    tree.mark = negate_mark[tree.mark]


class PolarizationPipeline:
    def __init__(self, sentences=None, verbose=0, parser="gum"):
        self.binarizer = Binarizer()
        self.polarizer = Polarizer()
        self.annotations = []
        self.annotated_sentences = []
        self.exceptioned = []
        self.incorrect = []
        self.verbose = verbose
        self.parser = parser
        self.sentences = sentences
        self.num_sent = 0 if sentences is None else len(sentences)

    def run_binarization(self, parsed, replaced, sentence):
        self.binarizer.parse_table = parsed[0]
        self.binarizer.postag = parsed[1]
        self.binarizer.words = parsed[2]

        if self.verbose == 2:
            print()
            print(parsed[0])
            print()
            print(parsed[1])
            print()
            print(replaced)

        self.binarizer.replaced = replaced
        binary_dep, relation = self.binarizer.binarization()
        if self.verbose == 2:
            self.postprocess(binary_dep)
        return binary_dep, relation

    def postprocess(self, tree, svg=False):
        sexpression = btree2list(tree, 0)
        if not svg:
            sexpression = '[%s]' % ', '.join(
                map(str, sexpression)).replace(",", " ").replace("'", "")
        # print(sexpression)
        return sexpression

    def run_polarization(self, binary_dep, relation, replaced, sentence):
        self.polarizer.dependtree = binary_dep
        self.polarizer.relation = relation
        self.polarizer.replaced = replaced

        self.polarizer.polarize_deptree()
        if self.verbose == 2:
            self.postprocess(binary_dep)
        elif self.verbose == 1:
            polarized = self.postprocess(binary_dep)
            svgling.draw_tree(polarized)
            # jupyter_draw_rsyntax_tree(polarized)
            #btreeViz = Tree.fromstring(polarized.replace('[', '(').replace(']', ')'))
            # jupyter_draw_nltk_tree(btreeViz)

    def modify_replacement(self, tree, replace):
        if str((tree.val, tree.id)) in replace:
            tree.val = replace[str((tree.val, tree.id))]

        if tree.is_tree:
            self.modify_replacement(tree.left, replace)
            self.modify_replacement(tree.right, replace)

    def single_polarization(self, sentence):
        parsed, replaced = dependency_parse(sentence, self.parser)
        # print(parsed)
        binary_dep, relation = self.run_binarization(
            parsed, replaced, sentence)
        # print(parsed)
        self.run_polarization(binary_dep, relation, replaced, sentence)
        annotated = self.polarizer.dependtree.sorted_leaves()

        if self.verbose == 2:
            annotated_sent = ' '.join([word[0] for word in annotated.keys()])
            self.annotated_sentences.append(annotated_sent)

        self.modify_replacement(self.polarizer.dependtree, replaced)

        return {
            'original': sentence,
            'annotated': annotated,
            'polarized_tree': self.polarizer.dependtree,
        }

    def batch_polarization(self, sentences):
        for i in tqdm(range(self.num_sent)):
            sent = sentences[i]
            try:
                annotation = self.single_polarization(sent)
                self.annotations.append(annotation)
            except Exception as e:
                if self.verbose == 2:
                    print(str(e))
                self.exceptioned.append(sent)
