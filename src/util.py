import heapq

from relation_priority import relationPriority

negate_mark = {
    "+": "-",
    "-": "+",
    "=": "="
}

det_mark = {
    "det:univ": ("+", "-"),
    "det:exist": ("+", "+"),
    "det:limit": ("+", "="),
    "det:negation": ("+", "-")
}

det_type_words = {
    "det:univ": ["all", "every", "each", "both"],
    "det:exist": ["a", "an", "some"],
    "det:limit": ["the", "this", "that", "those", "these", "my", "his", "her"],
    "det:negation": ["no", "neither"]
}

negtive_implicative = ["refuse", "reject", "oppose", "forget", "hesitate"]


def det_type(word):
    for det in det_type_words:
        if word.lower() in det_type_words[det]:
            return det


arrows = {
    "+": "\u2191",
    "-": "\u2193",
    "=": "=",
    "0": ""
}


def btreeToList(binaryDepdency, length, verbose=2):
    annotated = []

    def toList(tree):
        treelist = []
        if tree.getVal() not in relationPriority:
            treelist.append(tree.npos)
            if tree.getVal() == "n't":
                tree.val = "not"
            word = tree.getVal() + arrows[tree.mark]
            if verbose == 2:
                word += str(tree.key)
            index = tree.id
            heapq.heappush(annotated, (int(index), word))
            treelist.append(word)
        else:
            word = tree.getVal() + arrows[tree.mark]
            if verbose == 2:
                word += str(tree.key)
            treelist.append(word)

        left = tree.getLeft()
        right = tree.getRight()

        if left is not 'N':
            treelist.append(toList(left))

        if right is not 'N':
            treelist.append(toList(right))

        return treelist
    return toList(binaryDepdency), annotated


def convert2vector(result):
    result_vec = []
    if type(result) is "str":
        result_ls = result.split()
    else:
        result_ls = result
    for word in result_ls:
        if arrows['+'] in word:
            result_vec.append(1)
        elif arrows['-'] in word:
            result_vec.append(-1)
        elif arrows['='] in word:
            result_vec.append(0)
    return result_vec
