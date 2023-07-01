from math import log2
import sys
import csv

class Node:
    def __init__(self, feature, subtrees):
        self.feature = feature
        self.subtrees = subtrees

class Leaf:
    def __init__(self, value):
        self.value = value

def csv_train():
    with open("logic_small.csv", 'r') as f:
        text = csv.reader(f)
        header = next(text)
        train = []
        for line in text:
            train.append(line)
    #for a in train: print(a)
    return header, train

def csv_test():
    with open("logic_small_test.csv", 'r') as f:
        text = csv.reader(f)
        header = next(text)
        test = []
        for line in text:
            test.append(line)
    #for a in train: print(a)
    return test

def options(header, set, search):
    option = []
    for i in range(len(header)):
        if header[i] in search:
            option.append([])
            for j in range(len(set)):
                if set[j][i] not in option[-1]:
                    option[-1].append(set[j][i])
    return option

def frequencies(header, text, search):
    frequencies = []
    for i in range(len(header)):
        frequency_dict = {}
        frequencies.append(frequency_dict)

    for j in range(len(text)):
        for i in range(len(header)):
            value = text[j][i]
            if value in frequencies[i]:
                frequencies[i][value] += 1
            else:
                frequencies[i][value] = 1
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
    gain = round(gain, 3)
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
    print("\n")
    #print(header[gains.index(max(gains))])
    return feature[gains.index(max(gains))]

def print_tree(node, level=1, branch=""):
    tree_text = ""
    if isinstance(node, Leaf):
        tree_text += branch.lstrip() + " " + node.value + "\n"
    elif isinstance(node, Node):
        for i, (case, subtree) in enumerate(node.subtrees, start=1):
            new_branch = f"{branch} {level}:{node.feature}={case}"
            tree_text += print_tree(subtree, level + 1, new_branch)
    return tree_text

def check(example, tree, democratic):
    if isinstance(tree, Leaf):
        return tree.value
    elif isinstance(tree, Node):
        value = example[header.index(tree.feature)]
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
        m = possibilities.index(check(example, tree, democratic))
        n = possibilities.index(example[-1])
        matrix[n][m] += 1
    return matrix

def democratic_solution(header, train):
    f = frequencies(header, train, header[-1])
    maks = -1; solution = ""
    for key, value in f[0].items():
        if value > maks or (value == maks and key < solution): result = key
    return result

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
    subtrees = []
    option = options(header, set, x)
    i = header.index(x)
    new_list = []

    for j in remaining_options:
        if j != x:
            new_list.append(j)

    for case in option[0]:
        set1 = []
        for j in range(len(set)):
            if set[j][i] == case:
                set1.append(set[j])
        t = id3(set1, set, new_list, decision, header, current_level+1, limit)
        subtrees.append((case, t))
    #print(header, remaining_options, v, "c")
    return Node(x, subtrees)

header, train = csv_train()
test = csv_test()

democratic = democratic_solution(header, train)
id3_tree = id3(train, train, header[:-1], header[-1], header, 1, 1)
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

"""
def testing(header, text):
    print(header)
    for a in text: print(a)
    
    print("")
    options = []
    for i in range(len(header)):
        options.append([])
        for j in range(len(text)):
            if text[j][i] not in options[i]: options[i].append(text[j][i])
            print(text[j][i])
        print("")
    for i in range(len(header)): print(header[i], options[i])
    print("")

    frequencies = []
    for i in range(len(header)):
        frequency_dict = {}
        frequencies.append(frequency_dict)

    for j in range(len(text)):
        for i in range(len(header)):
            value = text[j][i]
            if value in frequencies[i]:
                frequencies[i][value] += 1
            else:
                frequencies[i][value] = 1

    for i in range(len(header)):
        print(header[i])
        for value, frequency in frequencies[i].items():
            print(value, frequency)
        print("")
"""