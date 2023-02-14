import xml.etree.ElementTree as ET 
import math



def parseXML(xmlfile):
    
    # print(xmlfile)
    # create element tree object
    tree = ET.parse(xmlfile)

    # get root element
    root = tree.getroot()
    sum = 0.0
    count = 0
    dur = []
    for i in root.findall('./tripinfo'):
        dur.append(float(i.get('duration')))
        sum = sum + float(i.get('duration'))
        count = count + 1
    maxval = max(dur)
    avg = sum/count
    var = 0
    for i in dur:
        var = var + ((float(i)-avg)**2)
    var= var/float(len(dur))
    print(avg,',',var**0.5,',',maxval)
    
    
parseXML('temp1')
