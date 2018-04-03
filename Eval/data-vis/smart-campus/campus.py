import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
matplotlib.rcParams.update({'font.size':36})

lines = open('smart-campus.csv', 'r')

devices = []
for line in lines:
	line = line.split(' ')
	devices.append(line[3])
devices = Counter(devices)
means = devices.values()

means = means[1:]

fig, ax = plt.subplots()
fig.tight_layout()
fig.subplots_adjust(left=0.15, right=0.95)
rects = ax.bar(np.arange(len(means)), means, 0.5, edgecolor='navy', fill=False, linewidth=6, log=True)
def autolabel(rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height),
                ha='center', va='bottom', fontsize=24)

autolabel(rects)
print devices.keys()[1:]

l = ['C4-Battery\n', 'Zigbee-Chann\n', 'C4-BV\n', 'system\n', 'Zigbee-Mac\n', 'Zigbee-NetSC\n', 'WebButton\n', 'C4-LightSens\n', 'C4-Motion\n', 'C4-Radio\n', 'C4-Temp\n']

plt.xticks(np.arange(len(means)), l, rotation='vertical', fontsize=32)
plt.ylim([0, 300000])
plt.ylabel('Count of Devices')
plt.xlabel('Type of Devices')
plt.subplots_adjust(bottom=0.4)
plt.grid(linestyle='dotted')
plt.show()
