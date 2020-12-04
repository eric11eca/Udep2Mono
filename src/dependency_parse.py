import corenlp
import os
import copy
import string
#from word2number import w2n

import stanza

nlp = stanza.Pipeline(
    "en",
    processors={"tokenize": "gum", "pos": "gum",
                "lemma": "gum", "depparse": "gum"},
    use_gpu=True,
    pos_batch_size=2000
)

os.environ["CORENLP_HOME"] = "./NaturalLanguagePipeline\lib\stanford-corenlp-4.1.0"

# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000

replacement = {
    "out of": "out-of",
    "none of the": "none-of-the",
    "all of the": "all-of-the",
    "some of the": "some-of-the",
    "most of the": "most-of-the",
    "many of the": "many-of-the",
    "several of the": "several-of-the",
    "some but not all": "some-but-not-all"
}


def preprocess(sentence):
    replaced = {}
    processed = sentence.lower()
    for orig in replacement:
        if orig in processed:
            processed = processed.replace(orig, replacement[orig])
            replaced[replacement[orig]] = orig
    return processed, replaced


def dependencyParse(sentence, parser="stanford"):
    processed, replaced = preprocess(sentence)
    if parser == "stanford":
        return stanfordParse(processed), replaced
    elif parser == "stanza":
        return stanzaParse(processed), replaced


def stanzaParse(sentence):
    postag = {}
    words = {}
    parsed = nlp(sentence)
    parse_tree = []
    for sent in parsed.sentences:
        for word in sent.words:
            tree_node = postProcess(sent, word, postag, words)
            if len(tree_node) > 0:
                parse_tree.append(tree_node)

    # for tree_node in parse_tree:
    #    printTree(tree_node, postag, words)
    return parse_tree, postag, words


def postProcess(sent, word, postag, words):
    wordID = int(word.id)
    if wordID not in words:
        postag[word.text] = (wordID, word.xpos)
        words[wordID] = (word.text, word.xpos)
    if word.deprel != "punct":
        tree_node = [word.deprel, wordID,
                     word.head if word.head > 0 else "root"]
        return tree_node
    return []


def printTree(tree, tag, word):
    if tree[0] != "root":
        print(
            f"word: {word[tree[1]][0]}\thead: {word[tree[2]][0]}\tdeprel: {tree[0]}",
            sep="\n",
        )


def stanfordParse(text):
    with corenlp.CoreNLPClient(
        annotators="tokenize ssplit pos lemma depparse".split()
    ) as client:
        ann = client.annotate(text)
        sentence = ann.sentence[0]
        words = {}
        for token in sentence.token:
            if not token.word in string.punctuation:
                words[token.tokenEndIndex] = [token.word, token.pos]

        deps = []
        targets = {}
        for edge in sentence.basicDependencies.edge:
            if edge.dep != "punct":
                targets[edge.target] = edge.dep
                deps.append([edge.dep, edge.target, edge.source])

        postags = {}
        maxroot = 0
        root = ""
        rooted = False

        for wordid in words:
            word = words[wordid][0]
            if not wordid in targets:
                if wordid > maxroot:
                    maxroot = wordid
                    root = wordid
                    rooted = True
                elif not rooted and "acl" in targets[wordid]:
                    maxroot = wordid
                    root = wordid
                    rooted = True
            postags[word] = [wordid, words[wordid][1]]
        deps.append(["root", root, "root"])

        for token in sentence.token:
            if not token.tokenEndIndex in words:
                words[token.tokenEndIndex] = [token.word, token.pos]
    return deps, postags, words
