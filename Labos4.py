import sys
import csv
import numpy
import random

# testne vrijednosti
trainset = "rosenbrock_train.txt"
testset = "rosenbrock_test.txt"
nn = "5s"
popsize = 10
elitism = 1
p = 0.5
k = 4.
iter = 6000

def csv_train(name):
    with open(name, 'r') as file:
        text = csv.reader(file)
        header = next(text)
        train = []
        for line in text:
            train.append(line)
    train_matrix = numpy.array(train)  # Pretvaranje liste u matricu
    return header, train_matrix

def csv_test(name):
    with open(name, 'r') as file:
        text = csv.reader(file)
        next(text)
        test = []
        for line in text:
            test.append(line)
    #for a in train: print(a)
    return test

def sigmoid(x):
    return 1 / (1+numpy.exp(-x))

def create_matrices(neurons_number):
    neurons = neurons_number.split("s")[:-1]
    neurons.append("1")
    matrices = []
    column = len(header)
    
    for neuron in neurons:
        matrix = numpy.random.normal(loc=0, scale = 0.01, size=(int(neuron), column))
        column = int(neuron)+1
        matrices.append(matrix)
    return matrices

def network(dataset, header, matrices):
    error = 0
    dataset = numpy.array(dataset)
    inputs = dataset[:, :-1].astype(float).T
    targets = dataset[:, -1].astype(float)
    num_examples = len(dataset)
    activations = [numpy.concatenate((inputs, numpy.ones((1, num_examples)))), ]
    for matrix in matrices[:-1]:
        new = numpy.dot(matrix, activations[-1])
        activations.append(sigmoid(new))
        activations[-1] = numpy.concatenate((activations[-1], numpy.ones((1, num_examples))))
    output = numpy.dot(matrices[-1], activations[-1])
    error = numpy.sum((targets-output)**2)
    return error / num_examples

def smallest_error(generation):
    a = []
    for gen in generation:
        a.append(network(train, header, gen))
    return min(a)

def goodest(generation):
    a = []
    for gen in generation:
        a.append(-network(train, header, gen))
    mini = min(a)
    for i in range(len(a)):
        a[i] = a[i] - mini
    suma = sum(a)
    random_num = suma / 5 + a[0]
    suma += len(a)*random_num
    for i in range(len(a)):
        a[i] = (a[i]+random_num)/suma
    return a

def choose_parents(generation):
    probabilities = goodest(generation)
    numbers = []
    for i in range(len(probabilities)):
        numbers.append(i)
    chosen = random.choices(numbers, probabilities, k=2)
    parents = []
    parents.append(generation[chosen[0]])
    parents.append(generation[chosen[1]])
    #print(chosen)
    return parents

def breed(parents):
    newborn = []
    for i in range(len(parents[0])):
        newborn.append((parents[0][i]+parents[1][i])/2)
    """
    print(parents[0])
    print()
    print(parents[1])
    print()
    print(newborn)
    """
    return newborn

def mutate(newborn, p, k):
    for i in range(len(newborn)):
        for j in range(len(newborn[i])):
            for l in range(len(newborn[i][j])):
                if(random.uniform(0,1) < p):
                    number = random.gauss(0, k)
                    newborn[i][j][l] += number
    return newborn

def genetic_algorithm(popsize, nn, elitism, p, k):
    generation = []
    for i in range(popsize):
        generation.append(create_matrices(nn))
    for i in range(1, iter+1):
        new_generation = []
        generation_temp = generation
        for j in range(elitism):
            good = goodest(generation_temp)
            new_generation.append(generation_temp[good.index(max(good))])
            generation_temp.pop(good.index(max(good)))
        while len(new_generation) < popsize:
            parents = choose_parents(generation)
            newborn = breed(parents)
            kid = mutate(newborn, p, k)
            new_generation.append(kid)
        generation = new_generation
        
        if i % 1000 == 0 or i == 1: 
            print(f"[Train error @{i}]: {smallest_error(generation)}")
    good = goodest(generation)
    print(f"[Test error]: {network(test, header, generation[good.index(max(good))])}")

header, train = csv_train(trainset)
test = csv_test(testset)
genetic_algorithm(popsize, nn, elitism, p, k)
