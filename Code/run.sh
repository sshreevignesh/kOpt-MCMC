#!/bin/bash

for i in {1..30}
do
    echo $alpha $iter $i
    cp "./kOptMCMC_Berkeley_results/newkoptmcmcmulti_Berkeley90A1000000I99l/output${i}" ../Maps/Berkeley/osm.passenger.trips.xml 
    # python3 findPathlength.py 5 7 >> KoptMCMC_Berkeley_pathlen.csv
    python3 generatepassengertrips.py ../Maps/Berkeley 2 15 7
    sumo.exe -c ../Maps/Berkeley/osm.sumocfg --additional-files additonalfile.add.xml --tripinfo-output temp1 
    python3 edgepollutionfileparser.py additionaloutput 7 >> KoptMCMC_90A1000000iterBerkeley_pollution.csv
    python3 tripinfoparser.py >> KoptMCMC_Berkeley_90A1000000itertripinfo.csv
done