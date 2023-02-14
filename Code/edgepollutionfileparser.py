import xml.etree.ElementTree as ET  
import csv
import sys
import sumolib 
sys.path.insert(1, '../Maps/Berkeley')
import sumoMCMCconfig as MCMCconfig

# def getnumsol(maxflow,vehperhour):
#     tree = ET.parse('../newnewHyderadab_demo/osm.passenger.trips.xml')
#     v = tree.getroot().findall('vehicle')
#     return len(v)/(maxflow*vehperhour)

def parseXML(xmlfile,net,numsol):
    
    edgewisepoll = {}
    for i in MCMCconfig.edgesID:
        edgewisepoll[MCMCconfig.edgesID[i]]=0

    tree = ET.parse(xmlfile)
    root = tree.getroot()
    edgeids = []
    nox = []
    
    for i in root.findall('./interval/edge'):
        edgeids.append(i.get('id'))
        nox.append(float(i.get('NOx_abs'))/numsol)
        edgewisepoll[i.get('id')]=float(i.get('NOx_abs'))/numsol

        
    print(sum(nox)/len(nox),end = ",")
    print(max(nox), end = ",")
    print(sum(nox), end = ",")
    print()
    # print("Mean Pollution: ",sum(nox)/len(nox))
    # print("Max Pollution: ",max(nox))
    # print("Total Pollution: ",sum(nox))
    # print()
    
    plot_nox = {}
    plotline_nox = {}
    
    for iter in MCMCconfig.edgesID:
        id = MCMCconfig.edgesID[iter]
        try:
            x = (net.getEdge(id).getFromNode().getCoord()[0] + net.getEdge(id).getToNode().getCoord()[0])/2
            y = (net.getEdge(id).getFromNode().getCoord()[1] + net.getEdge(id).getToNode().getCoord()[1])/2
            plot_nox[(x,y)]=0
            plotline_nox[id]=0
        except: 
            pass
        
    for iter in range(len(edgeids)):
        id = edgeids[iter]
        x = (net.getEdge(id).getFromNode().getCoord()[0] + net.getEdge(id).getToNode().getCoord()[0])/2
        y = (net.getEdge(id).getFromNode().getCoord()[1] + net.getEdge(id).getToNode().getCoord()[1])/2
        plot_nox[(x,y)]=nox[iter]
        plotline_nox[id]=nox[iter]
        
    
    # with open('nox_heatmap.csv', mode='w') as pollution_file:
    #     pollution_writer = csv.writer(
    #         pollution_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     pollution_writer.writerow(["Longitude", "Latitude", "Value"])
    #     for i in plot_nox:
    #         lon, lat = net.convertXY2LonLat(i[0], i[1])
    #         pollution_writer.writerow([lon, lat, plot_nox[i]])
    #     pollution_file.close()
    
    with open('nox_heatline.csv', mode='w') as pollution_file:
        pollution_writer = csv.writer(
            pollution_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        pollution_writer.writerow(["Fromlat","Fromlon","Tolat","Tolon", "Value"])
        for i in plotline_nox:
            p1 = net.getEdge(i).getFromNode().getCoord()
            p2 = net.getEdge(i).getToNode().getCoord()
            fromlon,fromlat = net.convertXY2LonLat(p1[0], p1[1])
            tolon,tolat = net.convertXY2LonLat(p2[0], p2[1])
            pollution_writer.writerow([fromlat,fromlon,tolat,tolon,plotline_nox[i]])
        pollution_file.close()
    
    # with open('face_heatmap.csv', mode = 'w') as pollution_file:
    #     pollution_writer = csv.writer(
    #         pollution_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     pollution_writer.writerow(["ID","Poll","geometry"])
    #     edgefacemap = {}
    #     for i in range(len(MCMCconfig.faces)):
    #         face = MCMCconfig.faces[i]
    #         for edge in face:
    #             if edge in MCMCconfig.edgesID:    
    #                 id = MCMCconfig.edgesID[edge]
    #                 if id in edgefacemap:
    #                     edgefacemap[id].append(i)
    #                 else:
    #                     edgefacemap[id]=[i]
    #             if (edge[1],edge[0]) in MCMCconfig.edgesID:
    #                 id = MCMCconfig.edgesID[(edge[1],edge[0])]
    #                 if id in edgefacemap:
    #                     edgefacemap[id].append(i)
    #                 else:
    #                     edgefacemap[id]=[i]
    #     facepoll = [0 for i in range(len(MCMCconfig.faces))]
    #     for i in plotline_nox:
    #         if plotline_nox[i]!=0:
    #             for j in edgefacemap[i]:
    #                 facepoll[j]+=plotline_nox[i]
        
    #     for i in range(len(facepoll)):
    #         facepoll[i] = facepoll[i]/len(MCMCconfig.faces[i])
    #         coords = []
    #         coords.append(net.getNode(MCMCconfig.faces[i][0][0]).getCoord())
    #         for edge in MCMCconfig.faces[i]:
    #             coords.append(net.getNode(edge[1]).getCoord())
    #         polygon = "POLYGON (("
    #         for j in coords:
    #             lon, lat = net.convertXY2LonLat(j[0],j[1])
    #             polygon = polygon + (str(lon))+ " "+str(lat)+", "
    #         polygon = polygon[:len(polygon)-2] + "))"
    #         pollution_writer.writerow([i,facepoll[i],polygon])
        
    #     # print(max(facepoll))
    
    #     pollution_file.close()
    
net = sumolib.net.readNet('../Maps/Berkeley/berkeley.net.xml')
parseXML(sys.argv[1],net,int(sys.argv[2]))
    
