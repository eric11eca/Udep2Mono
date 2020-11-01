from relation_priority import relationPriority


class BinaryDependencyTree:
    def __init__(self, val, parent, left, right, key, wid=None, npos=None):
        self.val = val
        self.parent = parent
        self.left = left
        self.right = right
        self.mark = "0"
        self.id = wid
        self.npos = npos
        self.key = key

    def isTree(self):
        return not (type(self.left) is str and type(self.right) is str)

    def getVal(self):
        return self.val

    def getLeft(self):
        return self.left

    def getRight(self):
        return self.right


class Binarizer:
    def __init__(self, parseTable=None, postag=None, words=None):
        self.postag = postag
        self.parseTable = parseTable
        self.words = words
        self.id = 0

    def process_not(self, children):
        if len(children) > 1:
            if children[0][0] == "advmod":
                if self.words[children[1][1]][0] == "not":
                    return [children[1]]
        return children

    def compose(self, head, parent):
        children = list(filter(lambda x: x[2] == head, self.parseTable))
        children.sort(key=(lambda x: relationPriority[x[0]]), reverse=True)
        children = self.process_not(children)
        if len(children) == 0:
            word = self.words[head][0]
            tag = self.words[head][1]
            binaryTree = BinaryDependencyTree(
                word, parent, "N", "N", self.id, head, tag)
            self. id += 1
            return binaryTree, [binaryTree.key]
        else:
            topDep = children[0]
        self.parseTable.remove(topDep)
        left, left_rel = self.compose(topDep[1], topDep[0])
        right, right_rel = self.compose(topDep[2], topDep[0])
        binaryTree = BinaryDependencyTree(
            topDep[0], parent, left, right, self.id)
        left_rel.append(binaryTree.key)
        self. id += 1
        return binaryTree, left_rel+right_rel

    def binarization(self):
        self.id = 0
        self.relation = []
        root = list(filter(lambda x: x[0] == "root", self.parseTable))[0][1]
        return self.compose(root, None)
