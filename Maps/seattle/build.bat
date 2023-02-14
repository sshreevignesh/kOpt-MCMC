#!/bin/bash
python "$SUMO_HOME/tools/randomTrips.py" -n osm.net.xml --fringe-factor 5 -p 0.366268 -o osm.passenger.trips.xml -e 36 --vehicle-class passenger --vclass passenger --prefix veh --min-distance 300 --trip-attributes "departLane=\"best\"" --fringe-start-attributes "departSpeed=\"max\"" --allow-fringe.min-length 1000 --lanes --validate
