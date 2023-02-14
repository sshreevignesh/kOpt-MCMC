import xml.etree.ElementTree as ET
import copy
import sys

# sys.path.insert(1, '../FullDelhiMap_LArge')
# import sumoMCMCconfig as MCMCconfig
path = sys.argv[1]
pass_file = path + "/osm.passenger.trips.xml"
tree = ET.parse(pass_file)
maxflow_value = int(sys.argv[2])

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
if len(samples) > 100:
    exit()
time_interval = int(sys.argv[3])
numsol = int(sys.argv[4])
samples=samples[:numsol]
f = open(pass_file, "w")
f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
f.write("<routes xmlns:xsi=\"http: // www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"http: // sumo.dlr.de/xsd/routes_file.xsd\">\n")
f.write("<vType id=\"veh_passenger\" vClass=\"passenger\"/>\n")
f.write("\n")
counter = 0
currtime = 0
for temp in samples:
    for temp_counter in range(int(3600/time_interval)):
        for flag in range(len(temp)):
            f.write("<vehicle id = \"veh" + str(counter) +
                    "\" type= \"veh_passenger\" depart=\"" + str(currtime) + "\" >\n")
            f.write("<route edges =\""+ temp[flag] +"\"/>\n")
            f.write("</vehicle>\n")
            counter = counter + 1
        currtime = currtime + time_interval
    currtime = currtime + 7200
f.write("</routes>\n")

