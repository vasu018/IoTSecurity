import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size':18})

# data to plot
n_groups = 10

frank= []
guido = []
faffa = []
maido = []
data = np.loadtxt('data.txt')
for run in data:
    frank.append(run[0])
    guido.append(run[1])
    faffa.append(run[2])
    maido.append(run[3])

# create plot
fig, ax = plt.subplots()
fig.tight_layout()
fig.subplots_adjust(left=0.1, right=0.95)
index = np.arange(n_groups)
bar_width = 0.2
opacity = 0.8

print index+bar_width 
rects1 = plt.bar(index, frank, bar_width,
                 alpha=opacity,
                 color='k',
                 label='#levels=2')
 
rects2 = plt.bar(index+bar_width, guido, bar_width,
                 alpha=opacity,
                 color='cyan',
                 label='#levels=3')

rects3 = plt.bar(index+bar_width+bar_width, faffa, bar_width,
                 alpha=opacity,
                 color='magenta',
                 label='#levels=4')
 
rects4 = plt.bar(index+bar_width+bar_width*2, maido, bar_width,
                 alpha=opacity,
                 color='yellow',
                 label='#levels=5')
 
plt.xlabel('# Leaf nodes (devices)')
plt.ylabel('Memory Utilization (GB)')
plt.xticks(index + bar_width*1.5, ('10k', '20k', '30k', '40k', '50k', '60k', '70k', '80k', '90k', '100k'))
plt.legend(loc='upper left', fontsize=18)
#plt.ylim([0.2, 2])
plt.grid(True)
plt.legend(loc = 'best', fontsize = 18)
plt.savefig("../Results/memory-abstraction.pdf", bbox_inches='tight')
plt.show()
plt.show()
#plt.savefig('memory-abstraction.pdf')
