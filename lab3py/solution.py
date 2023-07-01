from math import log2
import sys
import csv

class Node:
    def __init__(self, option, subtrees):
        self.option = option
        self.subtrees = subtrees

class Leaf:
    def __init__(self, decision):
        self.decision = decision

def csv_train(name):
    with open(name, 'r') as file:
        text = csv.reader(file)
        header = next(text)
        train = []
        for line in text:
            train.append(line)
    #for a in train: print(a)
    return header, train

def csv_test(name):
    with open(name, 'r') as file:
        text = csv.reader(file)
        next(text)
        test = []
        for line in text:
            test.append(line)
    #for a in train: print(a)
    return test

def options(header, set, search):
    option = []
    for j in range(len(header)):
        if header[j] in search:
            option.append([])
            for i in range(len(set)):
                if set[i][j] not in option[-1]:
                    option[-1].append(set[i][j])
    return option

def frequencies(header, text, search):
    frequencies = []
    for i in range(len(header)):
        frequency_dict = {}
        frequencies.append(frequency_dict)

    for i in range(len(text)):
        for j in range(len(header)):
            value = text[i][j]
            if value in frequencies[j]:
                frequencies[j][value] += 1
            else:
                frequencies[j][value] = 1
    i = 0; j = 0
    while i < len(header):
        if header[i] not in search:
            frequencies.pop(j)
            j -=1
        i += 1; j += 1
    return frequencies

def entropy(header, set, search):
    option = options(header, set, header)
    frequency = frequencies(header, set, header)
    gain = 0
    for key, value in frequency[-1].items():
        gain -= (value/len(set))*log2(value/len(set))
    gain = round(gain, 4)
    gains = []
    feature = []
    for i in range(len(header)-1):
        gain1 = gain
        #print(header[i])
        for j in range(len(option[i])):
            #print(option[i][j])
            set1 = []
            for k in range(len(set)):
                if set[k][i] == option[i][j]: set1.append(set[k])
            frequency1 = frequencies(header, set1, header)
            subset_entropy = 0
            for key, value in frequency1[-1].items():
                subset_entropy -= (value/len(set1))*log2(value/len(set1))
            #print(round(subset_entropy, 3))
            #for a in set1: print(a)
            gain1 -= len(set1)/len(set) * subset_entropy
        if(header[i] in search):
            gains.append(round(gain1, 4))
            feature.append(header[i])
    for i in range(len(gains)): print("IG(", header[i], ") = ", gains[i])
    #print(header[gains.index(max(gains))])
    return feature[gains.index(max(gains))]

def print_tree(node, level=1, branch=""):
    tree_text = ""
    if isinstance(node, Leaf):
        tree_text += branch.lstrip() + " " + node.decision + "\n"
    elif isinstance(node, Node):
        for i, (case, subtree) in enumerate(node.subtrees, start=1):
            new_branch = f"{branch} {level}:{node.option}={case}"
            tree_text += print_tree(subtree, level + 1, new_branch)
    return tree_text

def democratic_solution(header, train):
    f = frequencies(header, train, header[-1])
    maks = -1; solution = ""
    for key, value in f[0].items():
        if value > maks or (value == maks and key < solution): result = key
    return result

def check(example, tree, democratic):
    if isinstance(tree, Leaf):
        return tree.decision
    elif isinstance(tree, Node):
        value = example[header.index(tree.option)]
        for case, subtree in tree.subtrees:
            if case == value:
                return check(example, subtree, democratic)
    return democratic

def predict(test, tree, democratic):
    predictions = ""
    for example in test:
        result = check(example, tree, democratic)
        predictions += result + " "
    return predictions

def accuracy(test, tree, democratic):
    correct = 0
    for example in test:
        if check(example, tree, democratic) == example[-1]:
            correct += 1
    return format(correct/len(test), '.5f') #https://stackoverflow.com/a/22155830 kako zaokruziti na 5 iako bi py zaokruzio na jednu samo pa round nije dobar

def confusion_matrix(test, tree, train, header, democratic):
    possibilities = options(header, train, header[-1])
    possibilities = possibilities[0]
    if democratic not in possibilities: possibilities.append(democratic)
    possibilities.sort()
    matrix = [[0] * len(possibilities) for i in range(len(possibilities))]

    for example in test:
        n = possibilities.index(example[-1])
        m = possibilities.index(check(example, tree, democratic))
        matrix[n][m] += 1
    return matrix

def id3(set, parent_set, remaining_options, decision, header, current_level, limit):
    #print(header, remaining_options)
    if len(set) == 0:
        frequency = frequencies(header, parent_set, decision)
        maks = -1
        solution = ""
        for key, value in frequency[-1].items():
            if value > maks or (value == maks and key < solution):
                maks = value
                solution = key
        v = solution
        #print(header, remaining_options, v, "a")
        return Leaf(v)

    frequency = frequencies(header, set, decision)
    maks = -1
    solution = ""
    condition = False
    for key, value in frequency[-1].items():
        if value > maks or (value == maks and key < solution):
            maks = value
            solution = key
        if value == len(set):
            condition = True
    v = solution
    if len(remaining_options) == 0 or condition or current_level > limit:
        #print(header, remaining_options, v, "b")
        return Leaf(v)

    x = entropy(header, set, remaining_options)
    i = header.index(x)
    option = options(header, set, x)

    new_list = []
    for j in remaining_options:
        if j != x:
            new_list.append(j)

    subtrees = []
    for case in option[0]:
        set1 = []
        for j in range(len(set)):
            if set[j][i] == case:
                set1.append(set[j])
        t = id3(set1, set, new_list, decision, header, current_level+1, limit)
        subtrees.append((case, t))
    #print(header, remaining_options, v, "c")
    return Node(x, subtrees)

header, train = csv_train(sys.argv[1])
test = csv_test(sys.argv[2])
democratic = democratic_solution(header, train)
if len(sys.argv) == 3: id3_tree = id3(train, train, header[:-1], header[-1], header, 1, 10000)
elif len(sys.argv) == 4: id3_tree = id3(train, train, header[:-1], header[-1], header, 1, int(sys.argv[3]))
    
tree = print_tree(id3_tree, 1, "")
txt = "[BRANCHES]:\n" + tree
txt += "[PREDICTIONS]: " + predict(test, id3_tree, democratic)
txt += "\n[ACCURACY]: " + accuracy(test, id3_tree, democratic)
txt += "\n[CONFUSION_MATRIX]:\n"
matrix = confusion_matrix(test, id3_tree, train, header, democratic)
for i in range (len(matrix)):
    for j in range(len(matrix[i])):
        txt += str(matrix[i][j]) + " "
    txt = txt.rstrip() + "\n"
txt = txt.rstrip()
print(txt)
