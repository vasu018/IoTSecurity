import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size':45})

means = []

for i in range(5):
    d = np.loadtxt('data.txt', usecols=i, delimiter='\t')
    means.append(np.mean(d))

print means

ind = np.arange(5)  # the x locations for the groups
width = 0.3       # the width of the bars
fig, ax1 = plt.subplots()
rects1 = ax1.bar(ind, means, width, edgecolor='#00aff0', fill=False, linewidth=10, capsize=14)

#fig, ax = plt.subplots()
#index = np.arange(n_groups)
fig.tight_layout()
fig.subplots_adjust(left=0.12, right=0.95)
#
#bar_width = 0.2
#opacity = 0.8
#
#print index+bar_width 
#rects1 = plt.bar(index, frank, bar_width,
#                 alpha=opacity,
#                 color='magenta',
#                 label='#Elevelnodes=1000')
# 
#rects2 = plt.bar(index+bar_width, guido, bar_width,
#                 alpha=opacity,
#                 color='cyan',
#                 label='#Elevelnodes=2000')
#
#rects3 = plt.bar(index+bar_width+bar_width, faffa, bar_width,
#                 alpha=opacity,
#                 color='k',
#                 label='#Elevelnodes=5000')
# 
plt.xlabel('Depth', fontsize=40)
plt.ylabel('Latency (sec)', fontsize=40)
plt.xticks(ind, ('1', '2', '3', '4', '5'))
#plt.legend(loc='upper left', fontsize=40)
#plt.ylim([0, 3])
plt.grid(True)
plt.legend(loc = 'best', fontsize = 19)
plt.savefig("../Results/depth-latency.pdf", bbox_inches='tight')
plt.show()
plt.show()
