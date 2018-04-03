import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
matplotlib.rcParams.update({'font.size':36})

lines = open('Parking_meters.csv', 'r')

devices = []
meters_count = 0
for line in lines:
	meters_count += 1
        #print line[0], line[4], line[10], [11], line[15]
signals_count = 0
lines = open('Traffic_Signals.csv', 'r')
for line in lines:
	signals_count += 1

stations_count = 0
for i in range(2009, 2017):
	files = os.listdir(str(i))
	for f in files:
		lines = open(str(i)+'/'+f, 'r')
		for line in lines:
			stations_count += 1

lines = open('Stop_Signs.csv', 'r')
devices = []
signs_count = 0
for line in lines:
        signs_count += 1

lines = open('Bike_Share_Stations.csv', 'r')
devices = []
bike_count = 0
for line in lines:
        bike_count += 1

print meters_count
print signals_count
print stations_count

means = [meters_count, signals_count, stations_count, signs_count, bike_count]

print means

fig, ax = plt.subplots()
fig.tight_layout()
fig.subplots_adjust(left=0.1, right=0.95)
rects = ax.bar(np.arange(len(means)), means, 0.2, edgecolor='navy', fill=False, linewidth=6, log=True)
def autolabel(rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height),
                ha='center', va='bottom')

autolabel(rects)
#plt.xticks(np.arange(len(means)), devices.keys(), rotation='vertical', fontsize=24)
plt.ylim([10, 40000000])
plt.xticks(np.arange(len(means)), ['ParkingMeters', 'TrafficSignals', 'WeatherSts', 'TrafficSigns', 'BikeSts'], rotation='vertical', fontsize=32)
plt.ylabel('Count of Devices')
plt.xlabel('Type of Devices')
plt.subplots_adjust(bottom=0.4)
plt.grid(linestyle='dotted')
plt.show()
