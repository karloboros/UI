import argparse
import csv
import numpy
import random

def main(args):
    train_path = args.train
    test_path = args.test
    nn = args.nn
    popsize = int(args.popsize)
    elitism = int(args.elitism)
    p = float(args.p)
    k = float(args.K)
    iter = int(args.iter)

    header, train = csv_train(train_path)
    test = csv_test(test_path)
    genetic_algorithm(popsize, nn, elitism, p, k, train, test, header, iter)

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

def sigmoid(x):
    return 1 / (1+numpy.exp(-x))

def create_matrices(neurons_number, header):
    neurons = neurons_number.split("s")[:-1]
    neurons.append("1")
    matrices = []
    column = len(header)
    
    for neuron in neurons:
        matrix = numpy.random.normal(loc=0, scale = 0.01, size=(int(neuron), column))
        column = int(neuron)+1
        matrices.append(matrix)
    return matrices

def network(dataset, matrices):
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

def smallest_error(generation, train):
    a = []
    for gen in generation:
        a.append(network(train, gen))
    return min(a)

def goodest(generation, train):
    a = []
    for gen in generation:
        a.append(-network(train, gen))
    mini = min(a)
    for i in range(len(a)):
        a[i] = a[i] - mini
    suma = sum(a)
    for i in range(len(a)):
        a[i] = a[i]/suma
    return a

def choose_parents(generation, train):
    probabilities = goodest(generation, train)
    numbers = []
    for i in range(len(probabilities)):
        numbers.append(i)
    chosen = random.choices(numbers, probabilities, k=2)
    parents = []
    parents.append(generation[chosen[0]])
    parents.append(generation[chosen[1]])
    return parents

def breed(parents):
    newborn = []
    for i in range(len(parents[0])):
        newborn.append((parents[0][i]+parents[1][i])/2)
    return newborn

def mutate(newborn, p, k):
    for i in range(len(newborn)):
        for j in range(len(newborn[i])):
            for l in range(len(newborn[i][j])):
                if(random.uniform(0,1) < p):
                    number = random.gauss(0, k)
                    newborn[i][j][l] += number
    return newborn

def genetic_algorithm(popsize, nn, elitism, p, k, train, test, header, iter):
    generation = []
    for i in range(popsize):
        generation.append(create_matrices(nn, header))
    print(f"[Train error @0]: {smallest_error(generation, train)}")
    for i in range(1, iter+1):
        new_generation = []
        generation_temp = generation
        for j in range(elitism):
            good = goodest(generation_temp, train)
            new_generation.append(generation_temp[good.index(max(good))])
            generation_temp.pop(good.index(max(good)))
        while len(new_generation) < popsize:
            parents = choose_parents(generation, train)
            newborn = breed(parents)
            kid = mutate(newborn, p, k)
            new_generation.append(kid)
        generation = new_generation
        
        if i % 2000 == 0: 
            print(f"[Train error @{i}]: {smallest_error(generation, train)}")
    good = goodest(generation, train)
    print(f"[Test error]: {network(test, generation[good.index(max(good))])}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', required=True)
    parser.add_argument('--test', required=True)
    parser.add_argument('--nn', required=True, choices=['5s', '5s5s', '20s'])
    parser.add_argument('--popsize', required=True)
    parser.add_argument('--elitism', required=True)
    parser.add_argument('--p', required=True)
    parser.add_argument('--K', required=True)
    parser.add_argument('--iter', required=True)
    args = parser.parse_args()
    main(args)