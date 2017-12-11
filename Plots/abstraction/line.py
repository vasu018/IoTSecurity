import matplotlib
matplotlib.use('Agg')
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size':18})

runs = 10

policies = ['10000', '20000', '30000', '40000', '50000', '60000', '70000', '80000', '90000', '100000']
#policies = ['10k', '20k', '30k', '40k', '50k', '60k', '70k', '80k', '90k', '100k']

data_5 = {}
data_2 = {}
data_1 = {}
for p in policies:
    d = np.loadtxt(p+'.txt')
    for run in d:
        data_5.setdefault(p, []).append(run[0])
        data_2.setdefault(p, []).append(run[1])
        data_1.setdefault(p, []).append(run[2])
pd5 = []
pd2 = []
pd1 = []
for key in policies:
    pd5.append(np.mean(data_5[key]))
    pd2.append(np.mean(data_2[key]))
    pd1.append(np.mean(data_1[key]))

fig = plt.figure()
ax = fig.add_subplot(111)
fig.tight_layout()
fig.subplots_adjust(left=0.1, right=0.95)


tics = []
for p in policies:
    #tics.append(str(p[:-3])+'k')
    tics.append(str(p))

print pd5

ax.errorbar(tics, pd5, fmt='--o', label='#Elevelnodes=5000', linewidth=5, marker='s', markersize=15, color='b')
ax.errorbar(tics, pd2, fmt='--x', label='#Elevelnodes=2000', linewidth=5, marker='*', markersize=15, color='g')
ax.errorbar(tics, pd1, fmt='--*', label='#Elevelnodes=1000', linewidth=5, marker='o', markersize=15, color='cyan')
ax.legend(loc='upper left', numpoints=1, fontsize=18)
plt.xlabel('# Leaf nodes (devices)', fontsize=18)
plt.ylabel('Latency (ms)', fontsize=18)
#plt.xticks(range(len(tics)), [int(i)/1000 for i in policies], fontsize = 18)
plt.ylim([100, 850])
plt.grid(True)
plt.legend(loc = 'best', fontsize = 18)
plt.savefig("../Results/abstraction-latency.pdf", bbox_inches='tight')
plt.show()
