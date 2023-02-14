import numpy as np
import pandas as pd
import seaborn as sns
import folium
import webbrowser
from folium.plugins import HeatMap
import branca.colormap as cmp
import sys

filename = sys.argv[1]
mapname = sys.argv[2]
#seattle8831
maxpollmap = {"seattle": 5855, "Orzesze": 15215,
              "Hotan": 113810, "Kanpur": 8851, "Berkeley": 10230, "virtualseattle": 18245, "Islington": 13495, "virtualIslington": 13669, "smallmap": 19885, "hyd": 8295}

sources = {
    "smallmap": [],
    "virtualseattle": [(-122.31257019216338, 47.62763418964224), (-122.31815900582298, 47.61527157794472)],
    "seattle": [(-122.32235697387755, 47.628670931601896)],
    'smallmap': [(78.4372895433826, 17.378344303261347)],
    "Orzesze": [(18.826219590562413, 50.07740785782874)],
    "Kanpur": [(80.33059007826175, 26.404437357903625)],
    "Hotan": [(79.84722885108853, 37.309977116447364)],
    "Berkeley": [(-122.24386343547522, 37.857918240057735)],
    "Islington": [(-0.13097568058386766, 51.55920014701647)],       
    "virtualIslington": [(-0.13097568058386766, 51.55920014701647), (-0.08692968333672321, 51.54984121910383)],
    "hyd": [(78.37671454309461, 17.405629834782893)]
}
sinks = {
    "smallmap": [],
    "virtualseattle": [(-122.29687769080807, 47.61156592296453), (-122.29748887507799, 47.597394061992055)],
    "seattle": [(-122.29441737508361, 47.59920024994707)],
    'smallmap': [(78.43568130186374, 17.377034915943153)],
    "Orzesze": [(18.776701289543933, 50.15762620250127)],
    "Kanpur": [(80.29319116570765, 26.419361788744506)],
    "Hotan": [(79.95099228995218, 37.117247864538115)],
    "Berkeley": [(-122.26386036988818, 37.90362985375617)],
    "Islington": [(-0.08977202256146237, 51.52230796100811)],
    "virtualIslington": [(-0.08977202256146237, 51.52230796100811), (-0.11991578133891106, 51.53908937682658)],
    "hyd":[ (78.40285311375747, 17.380484026621986) ]
}

threshold = maxpollmap[mapname]
sources = sources[mapname]
sinks = sinks[mapname]


def getColor(colours, val, threshold):
    return colours[int(len(colours)*val/threshold)]


df = pd.read_csv(filename)
df = df.loc[df['Value'] != 0]
# print(df['Value'].describe(percentiles=[0.9, 0.95, 0.99, 0.995]))
# num = 1
fromlat = np.array(df['Fromlat'])
fromlon = np.array(df['Fromlon'])
tolat = np.array(df['Tolat'])
tolon = np.array(df['Tolon'])
poll = np.array(df['Value'], dtype=float)

maxval = max(poll)
colours = ['darkgreen', 'green', 'orange', 'red', 'purple', 'black']
gradient = {}
ind = 0
for val in range(int(threshold/6), threshold+1, int(threshold/6)):
    if val/maxval >= 1:
        gradient[1] = colours[ind]
        break
    gradient[val/maxval] = colours[ind]
    ind += 1
# print(gradient)

map_osm = folium.Map(location=[fromlat[0], fromlon[0]],
                     zoom_start=13, control_scale=True)

maxval = 15
for i in range(len(fromlat)):
    for j in range(maxval):
        col = getColor(colours, poll[i], threshold)
        folium.PolyLine(locations=[(fromlat[i], fromlon[i]), (tolat[i], tolon[i])], color=col,
                        no_clip=True, weight=j*2, opacity=(maxval-j)/maxval).add_to(map_osm)
for i in range(len(sources)):
    marker = folium.Marker(
        location=[sources[i][1], sources[i][0]], icon=folium.Icon(color="red"))
    marker.add_to(map_osm)

for i in range(len(sinks)):
    marker = folium.Marker(location=[sinks[i][1], sinks[i][0]])
    marker.add_to(map_osm)


file_path = "./test3.html"
map_osm.save(file_path)
# webbrowser.open(file_path)
