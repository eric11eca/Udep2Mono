import corenlp
import os
import copy
import string
from word2number import w2n

import stanza
nlp = stanza.Pipeline(
    'en', processors='tokenize,mwt,pos,lemma,depparse', use_gpu=False)

os.environ["CORENLP_HOME"] = "./NaturalLanguagePipeline\lib\stanford-corenlp-4.1.0"

# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000


def stanzaParse(sentence):
    postag = {}
    words = {}
    parsed = nlp(sentence)
    parse_tree = [postProcess(sent, word, postag, words)
                  for sent in parsed.sentences for word in sent.words]
    return parse_tree, postag, words


def postProcess(sent, word, postag, words):
    wordID = int(word.id)
    if wordID not in words:
        postag[word.text] = (wordID, word.xpos)
        words[wordID] = (word.text, word.xpos)
    tree_node = [word.deprel, wordID, word.head if word.head > 0 else "root"]
    #printTree(tree_node, postag[word.text])
    return tree_node


def printTree(tree, tag):
    print(
        f'word: {tree[1]}\thead: {tree[2]}\tdeprel: {tree[0]} \tid: {tag[0]} \txpos: {tag[1]}', sep='\n')


def dependencyParse(text):
    with corenlp.CoreNLPClient(annotators="tokenize ssplit pos lemma depparse".split()) as client:
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
        deps.append(['root', root, 'root'])
    return deps, postags, words
