import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size':45})

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
 
plt.xlabel('#PolicyIntents')
plt.ylabel('Memory Utilization (GB)')
plt.xticks(index + bar_width*1.5, ('1k', '2k', '3k', '4k', '5k', '6k', '7k', '8k', '9k', '10k'))
plt.legend(loc='upper left', fontsize=32)
#plt.ylim([0.2, 2])
plt.show()
#plt.savefig('memory-abstraction.pdf')
