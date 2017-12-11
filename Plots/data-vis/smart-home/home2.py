import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
matplotlib.rcParams.update({'font.size':36})

lines = open('smart-home.csv', 'r')

devices = []
for line in lines:
	line = line.split(',')
	device = line[0].split(':')
	devices.append(device[1])
devices = Counter(devices)
means = devices.values()

fig, ax = plt.subplots()
fig.tight_layout()
fig.subplots_adjust(left=0.1, right=0.95)
rects = ax.bar(np.arange(len(means)), means, edgecolor='navy', fill=False, linewidth=6)
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
plt.xticks(np.arange(len(means)), devices.keys(), rotation='vertical', fontsize=32)
plt.ylim([0, 125])
plt.ylabel('Count of Devices')
plt.xlabel('Type of Devices')
plt.subplots_adjust(bottom=0.4)
plt.grid(linestyle='dotted')
plt.show()
