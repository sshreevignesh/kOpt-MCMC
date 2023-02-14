import time
import copy
import random
import itertools 
import sys
import csv
import os


sys.path.insert(1, '..\Maps\Berkeley')
import sumoMCMCconfig as MCMCconfig


#Importing map data from the config file
s = MCMCconfig.s
t = MCMCconfig.t 
d = MCMCconfig.d
NumLanes = MCMCconfig.NumLanes
EdgeLength = MCMCconfig.EdgeLength
faces = MCMCconfig.faces

global count
paths = []


# Dijkstra's Algorithm to find path
def dijkstra(s, t, adjacency_list, currcapacity, NumLanes, EdgeLength):
    dist = {}
    for i in d.keys():
        dist[i] = float("Inf")
    dist[s] = 0
    parents = {}
    visited = {}
    q = set(adjacency_list.keys())
    for i in adjacency_list:
        parents[i] = None
        visited[i] = 0
    parents[s] = -1

    while q:
        curr = min(q, key=dist.get)
        q.remove(curr)
        visited[curr] = 1
        if curr == 'virtual_sink':
            break
        for adj in adjacency_list[curr]:
            if visited[adj] == 1:
                continue
            if (curr, adj) in NumLanes and NumLanes[(curr, adj)] > 0 and currcapacity[(curr, adj)] < NumLanes[(curr, adj)]:
                if curr == 'virtual_source' or adj == 'virtual_sink':
                    EdgeLength[(curr, adj)] = 0
                if EdgeLength[(curr, adj)] + dist[curr] < dist[adj]:
                    dist[adj] = EdgeLength[(curr, adj)] +  + dist[curr]
                    parents[adj] = curr

    if parents[t] == None:
        return None
    bfspath = []
    bfspath.append(t)
    i = t
    while parents[i] != -1:
        bfspath.append(parents[i])
        i = parents[i]
    return bfspath

#Breadth First search to find path
def capaciatatedBFS(s,t,adjacency_list,currcapacity,NumLanes):
    q = []
    q.append(s)
    visited = {}
    parents = {}
    for i in adjacency_list:
        visited[i] = 0
        parents[i] = None
    visited[s] = 1
    parents[s] = -1
    while len(q) > 0:
        curr = q[0]
        q.remove(curr)
        for i in adjacency_list[curr]:
            if visited[i] == 0:
                if (curr,i) in NumLanes and NumLanes[(curr,i)] > 0 and currcapacity[(curr,i)]<NumLanes[(curr,i)]:
                    visited[i] = 1
                    parents[i] = curr
                    q.append(i)
    if parents[t] == None:
        return None
    bfspath = []
    bfspath.append(t)
    i = t
    while parents[i] != -1:
        bfspath.append(parents[i])
        i = parents[i]
    return bfspath


# Function used to calculate Initial Max FLow solution. Implements the FFA algorithm and uses BFS or Dijkstra to find the augmenting path based on the parameter
def calculateMaxFlowCapacitated(s,t,adjacency_list,NumLanes, algo = 'BFS'):
    maxflow_value=0
    currcapacity = {}
    newNumlanes = copy.deepcopy(NumLanes)
    for i in NumLanes:
        currcapacity[i]=0
        if (i[1],i[0]) not in NumLanes:
            currcapacity[(i[1],i[0])]=0
            newNumlanes[(i[1],i[0])]=0
    
    if algo == 'BFS':
        currpath = capaciatatedBFS(s, t, adjacency_list, currcapacity,NumLanes)
        while currpath!=None:
            maxflow_value+=1
            for i in range(1,len(currpath)):
                currcapacity[(currpath[i-1],currpath[i])]-=1
                currcapacity[(currpath[i], currpath[i-1])]+=1
            currpath = capaciatatedBFS(s, t, adjacency_list, currcapacity,NumLanes)

    elif algo == 'Dijkstra':
        currpath = dijkstra(s, t, adjacency_list, currcapacity,NumLanes,MCMCconfig.EdgeLength)
        while currpath!=None:
            maxflow_value+=1
            for i in range(1,len(currpath)):
                currcapacity[(currpath[i-1],currpath[i])]-=1
                currcapacity[(currpath[i], currpath[i-1])]+=1
            currpath = dijkstra(s, t, adjacency_list, currcapacity,NumLanes,MCMCconfig.EdgeLength)

    return maxflow_value,currcapacity,newNumlanes


# Used to decompose a max flow solution into individual paths
def generatePathsFromMaxFlow(s,t,adjacency_list,flow_values):
    maxflow_paths= []
    currcapacity = {}
    
    #Since flow is allowed only in one direction for max flow, we set other direction flow as inf
    for i in flow_values:
        if flow_values[i]>0:
            currcapacity[i]=0
        else:
            currcapacity[(i[1],i[0])]=0
    
    currpath = capaciatatedBFS(s, t, adjacency_list, currcapacity,flow_values)

    while currpath!=None:
        for i in range(1,len(currpath)):
            currcapacity[(currpath[i],currpath[i-1])]+=1
        currpath.reverse()
        maxflow_paths.append(currpath)
        currpath = capaciatatedBFS(s,t, adjacency_list, currcapacity,flow_values)

        
    maxflowsol = []
    for path in maxflow_paths:
        newpath = []
        for i in range(len(path)-1):
            newpath.append((path[i], path[i+1]))
        maxflowsol.append(newpath)
        
    return maxflowsol


# Get the score of a max flow solution set based on the k_opt value and the path lengths
def get_val_kopt(k_opt_array,pathlength):
    maxval = k_opt_array[0][1]
    for i in k_opt_array:
        maxval = max(maxval,max(i))
    return alpha*pathlength+(1-alpha)*(maxval**3)

#Calculates the transition probabilities according to the Markov Chain rules
def calculate_probability_kopt(newpath,oldpath,lamda,currcapacity_array,k_opt_array,index,total_pathlength):
    val1 = get_val_kopt(k_opt_array,total_pathlength)
    for i in oldpath:
        if i not in newpath:
            total_pathlength -= MCMCconfig.EdgeLength[i]
            for j in range(len(currcapacity_array)):
                if j !=index:
                    k_opt_array[index][j]-=max(abs(currcapacity_array[j][i]),abs(currcapacity_array[j][(i[1],i[0])]))
    for i in newpath:
        if i not in oldpath:
            total_pathlength += MCMCconfig.EdgeLength[i]
            for j in range(len(currcapacity_array)):
                if j !=index:
                    k_opt_array[index][j]+=max(abs(currcapacity_array[j][i]),abs(currcapacity_array[j][(i[1],i[0])]))
    val2 = get_val_kopt(k_opt_array,total_pathlength)
    return min(1, lamda**(val2-val1)),total_pathlength

# Finds the path for the next iteration according to the given parameters
def find_new_path(edge, face, path, lamda, currcapacity, NumLanes,k_opt_array,index,total_pathlength):
    endIndexInFace = face.index(edge)
    endIndexInPath = path.index(edge)
    startIndexInFace = endIndexInFace
    startIndexInPath = endIndexInPath
    while face[endIndexInFace] == path[endIndexInPath]:
        endIndexInFace = (endIndexInFace+1) % len(face)
        endIndexInPath = (endIndexInPath+1) % len(path)

    prePath = path[0: startIndexInPath]
    midpath = []
    if endIndexInPath == 0:
        postPath = []
    else:
        postPath = path[endIndexInPath:]
    j = endIndexInFace
    while j != startIndexInFace:
        midpath.append((face[j][1], face[j][0]))
        j = (j+1) % len(face)
    midpath.reverse()
    
    newpath = prePath+midpath+postPath

    # Checking for cycles in the new path, the algo is supposed to ignore them as they will be irreversible
    isPathValid = True
    visitedNodes = []
    visitedNodes.append(newpath[0][0])
    for j in range(len(newpath)):
        if newpath[j][1] in visitedNodes:
            isPathValid = False
            break
        else:
            visitedNodes.append(newpath[j][1])

    # If the path is valid(no cycles), we update our current path
    if isPathValid:
        for edge in newpath:
            if edge[0]=='virtual_source' or edge[1]=='virtual_sink':
                continue
            if edge not in MCMCconfig.edgesID:
                return path,total_pathlength
            if currcapacity[edge]+1>NumLanes[edge]:
                return path,total_pathlength
        
        for edge in path[startIndexInPath:endIndexInPath]:
            if currcapacity[(edge[1], edge[0])] > NumLanes[(edge[1], edge[0])]:
                return path,total_pathlength

        probability, new_pathlen = calculate_probability_kopt(newpath,path,lamda,currcapacity_array,k_opt_array,index,total_pathlength)
        if random.random() <= probability:
            for i in range(len(k_opt_array)):
                k_opt_array[i][index] = k_opt_array[index][i]
            return newpath,new_pathlen
        else:
            for i in range(len(k_opt_array)):   
                k_opt_array[index][i] = k_opt_array[i][index]


    return path,total_pathlength

# Main Function
if __name__ == "__main__":

    runnumber = sys.argv[1]
    alpha = float(int(sys.argv[2]))/100.0
    num_iter = int(sys.argv[3])
    # lamda is a value between 0 and 1, telling us about the importance given to path length (1 means uniform distribution regardless of length, <1 means preference is given to shorter paths)
    lamda = float(int(sys.argv[4]))/100.0

    start_time = time.time()

    # time gap between two vehicles
    time_interval = 5
    num_sol = 7

    isMultiSource=False
    
    if isMultiSource:
        d['virtual_source'] = MCMCconfig.multisource
        d['virtual_sink'] = MCMCconfig.multisink
        s = 'virtual_source'
        t = 'virtual_sink'
        for source in MCMCconfig.multisource:
            NumLanes[('virtual_source',source)]= 1000
            EdgeLength[('virtual_source',source)] = 0
        for sink in MCMCconfig.multisink:
            if sink not in d:
                d[sink] = []
            d[sink].append('virtual_sink')
            EdgeLength[(sink,'virtual_sink')]=0
            NumLanes[(sink,'virtual_sink')]= 1000
        
    
    #Creating the initial max flow arrays using FFA(BFS) and FFA(Dijkstra)
    maxflow_value, currcapacity1, NumLanes = calculateMaxFlowCapacitated(s, t, d, NumLanes)  # calculateMaxFlow(s, t, d)
    maxflowsol1 = generatePathsFromMaxFlow(s, t, d, currcapacity1)    
    maxflows_array= []
    currcapacity_array = []
    for i in range(int(num_sol/2)):
        maxflows_array.append(copy.deepcopy(maxflowsol1))
        currcapacity_array.append(copy.deepcopy(currcapacity1))
    maxflow_value, currcapacity2, _ = calculateMaxFlowCapacitated(s, t, d, NumLanes,'Dijkstra')
    maxflowsol2 = generatePathsFromMaxFlow(s, t, d, currcapacity2)
    for i in range(int(num_sol/2),num_sol):
        maxflows_array.append(copy.deepcopy(maxflowsol2))
        currcapacity_array.append(copy.deepcopy(currcapacity2))

    #Initialisation
    numFaces = len(faces)
    combined_currcapacity = currcapacity_array[0]
    for i in range(1,len(currcapacity_array)):
        for j in combined_currcapacity:
            combined_currcapacity[j] += abs(currcapacity_array[i][j])

    #Initialising the array that stores the kOpt values
    k_opt_array = []
    for i in range(num_sol):
        k_opt_array.append([0 for j in range(7)])
    total_pathlength = 0
    for i in range(len(maxflows_array)):
        for j in range(len(maxflows_array[i])):
            for edge in maxflows_array[i][j]:
                total_pathlength+=MCMCconfig.EdgeLength[edge]
    for i in range(len(maxflows_array)):
        for j in range(i+1,len(maxflows_array)):
            flag = 0
            solution1 = maxflows_array[i]
            solution2 = maxflows_array[j]
            for path1 in solution1:
                for path2 in solution2:
                    for edge1 in range(len(path1)):
                        for edge2 in range(len(path2)):
                            if (path1[edge1][0] == path2[edge2][0] and path1[edge1][1] == path2[edge2][1]) or (path1[edge1][1] == path2[edge2][0] and path1[edge1][0] == path2[edge2][1]):
                                k_opt_array[i][j] +=1
                                k_opt_array[j][i] +=1


    # Iterating the steps of kOpt-MCMC Algorithm
    for i in range(num_iter):
      
        # We generate a random number between 0 and 1
        randomProbability = random.random()

        # With a probability of 0.5, stay in the same state
        if randomProbability > 0.5:
            continue

        # Choosing a random face and see if it has any common edge
        face = random.choice(faces)

        # Creating the same face in reverse order of edges
        reversedFace = face[:]
        reversedFace.reverse()
        for j in range(len(reversedFace)):
            reversedFace[j] = tuple(reversed(reversedFace[j]))


        #Choosing a random max flow solution from the set
        maxflow_index = random.choice(range(len(maxflows_array)))
        maxflowsol = maxflows_array[maxflow_index]
        currcapacity = currcapacity_array[maxflow_index]
        #Choosing a random path
        path_index = random.choice(range(len(maxflowsol)))
        isAdjacent = False

        for edge in maxflowsol[path_index]:
            currcapacity[edge] -= 1
            currcapacity[(edge[1], edge[0])] += 1
            
            combined_currcapacity[edge] -= 1
            combined_currcapacity[(edge[1], edge[0])] -= 1

        for edge in maxflowsol[path_index]:

            # If there is a common edge, we reroute through the face and find the new path
            if edge in face:
                isAdjacent = True
                maxflowsol[path_index],total_pathlength = find_new_path(
                    edge, face, maxflowsol[path_index], lamda, currcapacity, NumLanes,k_opt_array,maxflow_index,total_pathlength)
                break

            # Checking if the edge is there in reverse of the face
            # If there is a common edge, we reroute through the face and find the new path
            elif edge in reversedFace:
                isAdjacent = True
                maxflowsol[path_index],total_pathlength = find_new_path(
                    edge, reversedFace, maxflowsol[path_index], lamda, currcapacity, NumLanes,k_opt_array,maxflow_index,total_pathlength)
                break

        for edge in maxflowsol[path_index]:
            currcapacity[edge] += 1
            currcapacity[(edge[1], edge[0])] -= 1
            combined_currcapacity[edge] += 1
            combined_currcapacity[(edge[1], edge[0])] += 1
        
        maxflows_array[maxflow_index] = maxflowsol
        currcapacity_array[maxflow_index]= currcapacity

    if isMultiSource:
        for i in range(len(maxflows_array)):
            for j in range(len(maxflows_array[i])):
                maxflows_array[i][j]= maxflows_array[i][j][1:-1]
            
    exectime = (time.time() - start_time)
    
    final_kval = 0
    for i in range(len(k_opt_array)):
        final_kval = max(final_kval,max(k_opt_array[i]))
    time_interval = 5
    pathlength = 0

    for i in combined_currcapacity:
        if i[0] == 'virtual_source' or i[0] =='virtual_sink' or i[1] == 'virtual_source' or i[1] =='virtual_sink':
            continue
        pathlength += abs(combined_currcapacity[i])*EdgeLength[i]
    #since we consider both - and + for the same edge in curr capacity
    pathlength/=2 
    #since we are taking average len of path we divide by total number of mf solutions and paths per mf solution
    pathlength = pathlength/(num_sol* maxflow_value)
    filepath = "newkoptmcmcmulti_berkeley" 
    if isMultiSource:
        filepath = filepath+"virtual"
    
    with open(filepath + 'numsol.csv',mode = 'a') as f:
        fwriter = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        fwriter.writerow([alpha,lamda,num_iter,pathlength,final_kval,exectime])
        f.close() 
        
    filepath1 = filepath + str(int(alpha*100))+"A" + str(num_iter) + "I" + str(int(lamda*100)) + "l"
    if os.path.exists(filepath1) == False:
        os.makedirs(filepath1)
    f = open(filepath1 + "/output"+str(runnumber), "w")
    f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    f.write("<routes xmlns:xsi=\"http: // www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"http: // sumo.dlr.de/xsd/routes_file.xsd\">\n")
    f.write("<vType id=\"veh_passenger\" vClass=\"passenger\"/>\n")
    f.write("\n")
    counter = 0
    currtime = 0
    for temp in maxflows_array:
        for flag in range(len(temp)):
            f.write("<vehicle id = \"veh" + str(counter) +
                "\" type= \"veh_passenger\" depart=\"" + str(currtime) + "\" >\n")
            f.write("<route edges =\"")
            for edge in temp[flag]:
                if edge[0] =='virtual_source' or edge[1]=='virtual_sink' or edge[0]=='virtual_sink' or edge[1] =='virtual_source':
                    continue
                if edge in MCMCconfig.edgesID:
                    f.write(" "+MCMCconfig.edgesID[edge])
                else:
                    f.write(" "+MCMCconfig.edgesID[(edge[1], edge[0])])
            f.write("\"/>\n")
            f.write("</vehicle>\n")
            counter = counter + 1
        currtime = currtime + time_interval
        currtime = currtime + 3600   
    f.write("</routes>\n")



    
