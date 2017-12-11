import json
import os
import numpy as np
import matplotlib.pyplot as plt

runs = 10

policies = ['1000', '2000', '3000', '4000', '5000', '6000', '7000', '8000', '9000', '10000', '11000', '12000']

data_5 = {}
data_2 = {}
data_1 = {}
for p in policies:
    d = np.loadtxt('l_'+p+'.txt')
    for run in d:
        data_5.setdefault(p, []).append(run[0])
        data_2.setdefault(p, []).append(run[1])
        data_1.setdefault(p, []).append(run[2])
pd5 = []
pd2 = []
pd1 = []
for key in policies:
    pd5.append(data_5[key])
    pd2.append(data_2[key])
    pd1.append(data_1[key])
fig = plt.figure()
ax = fig.add_subplot(111)

def plot(pd, c):
    bp = ax.boxplot(pd, 0, ' ', widths=0.3)
    for box in bp['boxes']:
        box.set( color=c, linewidth=1)
    
#    for whisker in bp['whiskers']:
#        whisker.set(color='b', linewidth=1)
#    
#    for cap in bp['caps']:
#        cap.set(color='r', linewidth=1)
#    
#    for median in bp['medians']:
#        median.set(color='k', linewidth=1)
plot(pd5, 'b') 
#plot(pd5, 'g', np.array(xrange(len(pd5)))*2.0-0.1) 
#plot(pd2, 'b', np.array(xrange(len(pd5)))*2.0) 
#plot(pd1, 'r', np.array(xrange(len(pd5)))*2.0+0.1) 
    
ax.set_ylabel('Latency (ms)', fontsize=16)
ax.set_xlabel('#Policies', fontsize=16)
ax.set_xticklabels(['1000', '2000', '3000', '4000', '5000', '6000', '7000', '8000', '9000', '10000', '11000', '12000'])

plt.savefig('composition-latency.pdf')
