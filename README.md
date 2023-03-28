# kOpt-MCMC
 
## Instructions to run

There are data files available for 4 maps (Seattle, Berkeley, Islington and Kanpur). The main code file is `kOptMCMC.py`. In order to change the input map, modify the following code in the file

```
sys.path.insert(1, '..\Maps\Berkeley')
filepath = "kOptMCMC_berkeley" 
```

Replace the First line with the Path to the Map source folder. The second variable will be used as a prefix to the output files and therefore it is recommended to update the map name there too in order to avoid confusion


Use the following command to run the files setting the value of the 4 parameters
```
python3 kOptMCMC.py <runnumber> <alpha*100> <num_iter> <lambda *100 >
```
here, `runnumber` is an identifer we used to prevent the overwriting of the output files when we run the code multiple times using the same parameters. If we want 30 runs with the same parameters, we can run the above command 30 times modifying only the runnumber and we will have all the 30 outputs

`alpha * 100` is the value of alpha multiplied by 100. For example, if alpha is 0.5 then the value will be 50, if alpha is 0.01 then it will be 1 etc.

`num_iter` is the number of iterations we wnat our algorithm to run for.

`lambda * 100` is the value of lambda multipled by 100.if lambda is 0.5 then the value will be 50, if lambda is 0.01 then it will be 1 etc.

The above code will generate the paths and save it in the following folder

`filepath + str(int(alpha*100))+"A" + str(num_iter) + "I" + str(int(lamda*100)) + "l"`

Here `filepath` is a prefix you can modify in the `kOptMCMC.py` file

Once we have the output, we need to convert it to `passengers.trips.xml` file for SUMO and we need to run the following command for that 
```
cp <kOptMCMC output file> ../Maps/<Mapname>/osm.passenger.trips.xml
python3 generatepassengertrips.py ../Maps/<Mapname> <MaxFlow Value>
```

This will generate the passenger.trips file which can be used to start the SUMO simulations. The command for the same is as follows 
```
sumo -c ..\Maps\<Map name>\osm.sumocfg --additional-files additonalfile.add.xml
```

This will run the SUMO simulations and will generate the pollution output. The output can be parsed using the following command (Do note that you have to change the paths within the code file for the corresponding Maps)

```
python3 edgepollutionfileparser.py additionaloutput 7
```

This will print the Mean,Max and Total pollution for the simulation. In order to generate the Heatmaps, we can run the following command 

```
python3 generateHeatlines.py nox_heatline.csv <MapName>
```
The above command will create the heatmap and save it as an HTML file. In order to recreate the heatmaps in the paper, you can use the `Heatmapfiles` folder, and replace `nox_heatline.csv` with the corresponding file for the map you want to use