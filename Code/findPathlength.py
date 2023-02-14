import xml.etree.ElementTree as ET
import copy
import sys
import sumolib

sys.path.insert(1, '../Maps/Islington')
import sumoMCMCconfig as MCMCconfig

path = '../Maps/Islington'
pass_file = path + "/osm.passenger.trips.xml"
tree = ET.parse(pass_file)
maxflow_value = int(sys.argv[1])

# get root element
root = tree.getroot()
samples = []
currsol = []
# print(len(root.findall('./vehicle/route')))
for i in root.findall('./vehicle/route'):
    currsol.append(i.get('edges'))
    if len(currsol) == maxflow_value:
        samples.append(copy.deepcopy(currsol))
        currsol = []

# print(len(samples))
numsol = int(sys.argv[2])
samples=samples[:numsol]

edgemap = {}
for i in MCMCconfig.edgesID:
    edgemap[MCMCconfig.edgesID[i]] = i
totallen = 0
for sample in samples:
    pathlen = 0
    # prevpathlen=0
    for path in sample:
        path1=path.split(" ")
        for edge in path1:
            if edge=="":
                continue
            try:
                pathlen+=MCMCconfig.EdgeLength[edgemap[edge]]
            except:
                pathlen+=MCMCconfig.EdgeLength[(edgemap[edge][1],edgemap[edge][0])]
            
        # prevpathlen= pathlen
        # print(pathlen-prevpathlen)
    pathlen/= len(sample)
    totallen+=pathlen
    
print(totallen/numsol)
