import argparse

def main(args):
    alg = args.alg
    states_file = args.ss
    heuristic_file = args.h
    check_optimistic = args.check_optimistic
    check_consistent = args.check_consistent

    start, final, succ = succesor(states_file)
    h = heuristic(heuristic_file)
    if alg == 'bfs':
        bfsSearch(start, succ, final)
    elif alg == 'ucs':
        ucsSearch(start, succ, final)
    else:
        aStarSearch(start, succ, final, h)
    if check_optimistic:
        isOptimistic(succ, final, h)
    if check_consistent:
        isConsistent(succ, h)

def succesor(name):
    succ = {}
    with open(name, 'r', encoding='utf-8') as f:
        startBool, finalBool = False, False
        for line in f:
            line = line.rstrip()
            #print(line)
            if line.startswith('#'): continue
            elif startBool == False or finalBool == False:
                if startBool == False:
                    start = line
                    startBool = True
                elif finalBool == False:
                    final = line.split(' ')
                    finalBool = True
            elif ':' in line:
                key, value_str = line.split(':')
                inner_dict = {}
                for inner_str in value_str.split():
                    inner_key, inner_value = inner_str.split(',')
                    inner_dict[inner_key] = int(inner_value)
                succ[key] = inner_dict
    return start, final, succ

def heuristic(name):
    h = {}
    with open(name, 'r', encoding='utf-8') as f:
        for line in f:
            #print(line)
            if ':' in line:
                key, value = line.strip().split(':')
                h[key] = int(value)
    return h

def bfsSearch(s0, succ, goal):
    open = [(s0, 0, None)]
    closed = []
    visited = 0
    visited_states = []
    while open:
        n = open[0]
        open.pop(0)
        visited += 1
        closed.append(n)
        if n[0] in goal: 
            states = []
            closed.reverse()
            cost = closed[0][1]
            search = n[0]
            for state in closed:
                if state[0] == search and state[0] != state[2]: 
                    states.append(state[0])
                    search = state[2]
                elif search == 'None': break
            
            states.reverse()
            path = " => ".join(states)
            txt = ''
            txt += "# BFS file.txt" + "\n"
            txt += "[FOUND_SOLUTION]: yes" + "\n"
            txt += "[STATES_VISITED]: " + str(len(closed)) + "\n"
            txt += "[PATH_LENGTH]: " + str(len(states)) + "\n"
            txt += "[TOTAL_COST]: " + str(float(cost)) + "\n"
            txt += "[PATH]: " + path + "\n"
            print(txt)
            return txt
        visited_states.append(n[0])
        temp = []
        for key, value in succ[n[0]].items():
            #print(key)
            if key in visited_states: continue
            temp += [(key, value+n[1], n[0])]
            temp = sorted(temp, key = lambda x: (x[0]))
        open += temp
        #print(visited, n[0], n[1], open)
    txt = "# BFS istra.txt\n[FOUND_SOLUTION]: no"
    print(txt)
    return txt

def ucsSearch(s0, succ, goal):
    open = [(s0, 0, None)]
    closed = []
    visited = 0
    visited_states = []
    while open:
    #for i in range(10):
        n = open[0]
        open.pop(0)
        visited += 1
        closed.append(n)
        if n[0] in goal: 
            #print(closed)
            states = [n[0]]
            closed.reverse()
            cost = closed[0][1]
            curr_cost = cost
            search = n[2]
            for state in closed:
                if state[0] == search and state[0] != state[2] and curr_cost == succ[search][states[-1]]+state[1]: 
                    states.append(state[0])
                    search = state[2]
                    curr_cost = state[1]
                elif search == 'None': break

            states.reverse()
            path = " => ".join(states)
            txt = ''
            txt += "# UCS file.txt" + "\n"
            txt += "[FOUND_SOLUTION]: yes" + "\n"
            txt += "[STATES_VISITED]: " + str(len(closed)) + "\n"
            txt += "[PATH_LENGTH]: " + str(len(states)) + "\n"
            txt += "[TOTAL_COST]: " + str(float(cost)) + "\n"
            txt += "[PATH]: " + path + "\n"
            print(txt)
            return txt
        visited_states.append(n[0])
        #print(visited_states)
        for key, value in succ[n[0]].items():
            if key == n[2] or key in visited_states: continue
            open += [(key, value+n[1], n[0])]
            open = sorted(open, key = lambda x: x[1])
        #print(n[0], n[1], open,"\n")
    txt = "# UCS istra.txt\n[FOUND_SOLUTION]: no"
    print(txt)
    return txt

def aStarSearch(s0, succ, goal, h):
    open = [(s0, 0, 0, None)]
    closed = []
    visited = 0
    visited_states = []
    while open:
        n = open[0]
        open.pop(0)
        visited_states.append(n[0])
        visited += 1
        if n[0] in goal: 
            states = [n[0]]
            closed.reverse()
            cost = n[1]
            curr_cost = cost
            search = n[3]
            for state in closed:
                if state[0] == search and state[0] != state[3] and curr_cost == succ[search][states[-1]]+state[1]: 
                    states.append(state[0])
                    search = state[3]
                    curr_cost = state[1]
                elif search == 'None': break
            
            states.reverse()
            path = " => ".join(states)
            txt = ''
            txt += "# A-STAR file.txt" + "\n"
            txt += "[FOUND_SOLUTION]: yes" + "\n"
            txt += "[STATES_VISITED]: " + str(visited) + "\n"
            txt += "[PATH_LENGTH]: " + str(len(states)) + "\n"
            txt += "[TOTAL_COST]: " + str(float(cost)) + "\n"
            txt += "[PATH]: " + path + "\n"
            print(txt)
            return txt
        closed.append(n)
        for key, value in succ[n[0]].items():
            flag = False
            i = 0
            mix = closed+open
            for state in mix:
                if key == state[0]: 
                    flag = True
                    break
                i += 1
            if flag:
                #print(key, value + n[1], mix[index], "\n",index, mix)
                #print(key, value+n[1], mix[index][1])
                if value+n[1] > mix[i][1]: continue
                else: mix.pop(i)
            open += [(key, value+n[1], value+n[1]+h[key], n[0])]
            open = sorted(open, key = lambda x: x[2])
        #print(n[0], n[1], open,"\n")
        #print(closed,"\n")
    txt = "# A* file.txt\n[FOUND_SOLUTION]: no"
    print(txt)
    return

def ucsSearchOptimistic(s0, succ, goal):
    open = [(s0, 0, None)]
    closed = []
    visited = 0
    visited_states = []
    while open:
        n = open[0]
        open.pop(0)
        visited += 1
        closed.append(n)
        if n[0] in goal: 
            closed.reverse()
            cost = closed[0][1]
            return float(cost)
        visited_states.append(n[0])
        for key, value in succ[n[0]].items():
            if key == n[2] or key in visited_states: continue
            open += [(key, value+n[1], n[0])]
            open = sorted(open, key = lambda x: x[1])
    return -1

def isOptimistic(succ, goal, h):
    optimistic = True
    txt = ''
    list = []
    for key in succ:
        list.append(key)
    list.sort()
    for key in list:
        calculated = ucsSearchOptimistic(key, succ, goal)
        value = float(h[key])
        txt += "[CONDITION]: "
        if value > calculated or calculated < 0: 
            txt += "[ERR] "
            optimistic = False
        else: txt += "[OK] "
        txt += f"h({key}) <= h*: {value} <= {calculated}\n"
    if optimistic:
        txt += "[CONCLUSION]: Heuristic is optimistic."
    else:
        txt += "[CONCLUSION]: Heuristic is not optimistic."
    print(txt)
    return

def isConsistent(succ, h):
    txt = ''
    consistent = True
    for key in succ:
        for next, value in succ[key].items():
            txt += "[CONDITION]: "
            if h[key] > h[next] + value:
                consistent = False
                txt += "[ERR] "
            else:
                txt += "[OK] "
            txt += f"h({key}) <= h({next}) + c: {float(h[key])} <= {float(h[next])} + {float(value)}\n"
    if consistent:
        txt += "Heuristic is consistent"
    else:
        txt += "Heuristic is not consistent"
    print(txt)
    return

#print("start: ", start, "\nfinal: ", final, "\n")
#bfsSearch(start, succ, final)
#ucsSearch(start, succ, final)
#aStarSearch(start, succ, final, h)
#isOptimistic(succ, final, h)
#isConsistent(succ, h)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--alg', required=True, choices=['bfs', 'ucs', 'astar'])
    parser.add_argument('--ss', required=True)
    parser.add_argument('--h', required=True)
    parser.add_argument('--check-optimistic', action='store_true')
    parser.add_argument('--check-consistent', action='store_true')
    args = parser.parse_args()
    main(args)