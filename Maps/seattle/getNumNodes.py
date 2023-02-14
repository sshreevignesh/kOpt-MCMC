import sumoMCMCconfig

numnodes = 0
numedges = 0
d = sumoMCMCconfig.d
for i in d:
    numnodes +=1
    numedges += len(d[i])
    
print(numnodes,numedges)