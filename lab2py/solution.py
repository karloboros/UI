import sys

def listClauses(name):
    clauses = []
    with open(name, 'r', encoding = 'utf-8') as f:
        text = f.readlines()
        for line in text:
            line = line.rstrip()
            line = line.lower()
            if line.startswith('#'): continue
            clauses.append(line)
    return clauses

def listUserCommands(name):
    commands = []
    with open(name, 'r', encoding = 'utf-8') as f:
        text = f.readlines()
        for line in text:
            line = line.rstrip()
            line = line.lower()
            if line.startswith('#'): continue
            task = line[-1]
            clause = line[:-1].rstrip()
            commands += [(clause, task)]
    return commands

def resolution(clauses, final, flag):
    result = False
    update = erase(clauses)
    neg_final = negation(final)
    
    broj = 1
    txt = ''
    temp = []
    new_clauses = []
    for clause in update: 
        if(len(clause) == 0): continue
        txt += str(broj) + ". " + clause + '\n'
        broj += 1
        temp.append(clause.split(' v '))
        #new_clauses += [(clause,"0","0")]
    update = temp
    temp = []
    for clause in neg_final: 
        if(len(clause) == 0): continue
        txt += str(broj) + ". " + clause + '\n'
        broj += 1
        temp.append(clause.split(' v '))
        #new_clauses += [(clause,"0","0")]
    neg_final = temp
    txt += "===============\n"


    new = True
    while new and not result:
        new = False

        for each1 in neg_final:
            if result: break
            for each2 in neg_final+update:
                if result: break
                if each1 == each2: continue
                for elem1 in each1:
                    if result: break
                    for elem2 in each2:
                        if '~' + elem1 == elem2 or '~' + elem2 == elem1:
                            new = True
                            temp = []
                            for elem in each1: 
                                if(elem != elem1): temp.append(elem)
                            for elem in each2: 
                                if(elem != elem2): temp.append(elem)
                            if len(temp) == 0: 
                                result = True
                                new_clauses += [('NIL', ' v '.join(each1), ' v '.join(each2))]
                            else: 
                                new_clauses += [(' v '.join(temp), ' v '.join(each1), ' v '.join(each2))]
                                neg_final.append(temp)
                                neg_final, update = eraseResolution(neg_final, update)

    if result: 
        new_clauses.reverse()
        search1 = new_clauses[0][1]
        search2 = new_clauses[0][2]
        print_clauses = [new_clauses[0]]
        for elem in new_clauses:
            if elem[0] == search1 or elem[0] == search2:
                print_clauses += [elem]
                search1 = elem[1]
                search2 = elem[2]
        print_clauses.reverse()
        for elem in print_clauses:
            txt += str(broj) + ". " + elem[0] + " (" + elem[1] + ", " + elem[2] + ")\n"
            broj += 1
        txt += "===============\n"
        txt +="[CONCLUSION]: " + final + " is true"
    else: 
        txt ="[CONCLUSION]: " + final + " is unknown"

    if not flag: print(txt)
    else: return txt
    return

def cooking(clauses, user_commands):
    txt = 'Constructed with knowledge:\n'
    for clause in clauses:
        txt += clause + '\n'
    print(txt)
    for command in user_commands:
        var = ''.join(command[0])
        txt = ''
        txt += "User's command: " + var + " " + command[1] + '\n'
        if(command[1] == '?'):
            txt += resolution(clauses, command[0], 1) + '\n'
        elif(command[1] == '-'):
            for clause in clauses:
                if clause == command[0]:
                    clauses.remove(clause)
            txt += "removed " + command[0] + '\n'
        elif(command[1] == '+'):
            clauses.append(command[0])
            txt += "Added " + command[0] + '\n'
        print(txt)
    return 

def negation(final):
    negated = []
    final = final.split(' ')
    if len(final) == 1:
        if(final[0].startswith('~')): negated.append(final[0][1:])
        else: text = '~' + final[0]; negated.append(text)
    else:
        for word in final:
            if(word == 'v'): continue
            if word.startswith('~'): word = word[1:]
            else: word = '~' + word
            negated.append(word)
    return negated

def erase(clauses):
    new =[]
    for clause in clauses: new.append(clause.split(' v '))
    
    i = -1; j = 0
    while i < len(new)-2:
        i += 1; j = i
        #if(len(new[i]) == 1): continue
        while j < len(new)-1:
            j += 1
            #if(len(new[j]) == 1): continue
            if all(elem in new[i] for elem in new[j]): 
                new.pop(i); i -= 1; j = len(new)
            elif all(elem in new[j] for elem in new[i]): 
                new.pop(j); j -= 1
                
    i = -1
    while i < len(new)-1:
        i += 1; tautology = False
        for j in range(0, len(new[i])-1):
            for k in range(j+1, len(new[i])):
                if(new[i][j] == '~' + new[i][k] or '~' + new[i][j] == new[i][k]): 
                    tautology = True; break
            if tautology: break
        if tautology: 
            new.pop(i); i -=1
    
    clauses = []
    for clause in new: clauses.append(' v '.join(clause))

    return clauses

def eraseResolution(final, update):
    new =[]
    new = final + update
    
    i = -1; j = 0
    while i < len(new)-2:
        i += 1; j = i
        while j < len(new)-1:
            j += 1
            if all(elem in new[i] for elem in new[j]): 
                new.pop(i); i -= 1; j = len(new)
            elif all(elem in new[j] for elem in new[i]): 
                new.pop(j); j -= 1
                
    i = -1
    while i < len(new)-1:
        i += 1; tautology = False
        for j in range(0, len(new[i])-1):
            for k in range(j+1, len(new[i])):
                if(new[i][j] == '~' + new[i][k] or '~' + new[i][j] == new[i][k]): 
                    tautology = True; break
            if tautology: break
        if tautology: 
            new.pop(i); i -=1
    
    final1 = []; update1 = []
    for clause in new:
        if clause in final:
            final1.append(clause)
        elif clause in update:
            update1.append(clause)

    return final1, update1

if sys.argv[1] == "resolution":
    clauses = listClauses(sys.argv[2])
    resolution(clauses[:-1], clauses[-1], 0)
elif sys.argv[1] == "cooking":
    clauses = listClauses(sys.argv[2])
    user_commands = listUserCommands(sys.argv[3])
    cooking(clauses, user_commands)