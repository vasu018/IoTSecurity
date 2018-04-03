import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size':45})

# data to plot
n_groups = 16

frank= []
guido = []
faffa = []
data = np.loadtxt('data.txt')
for run in data:
    frank.append(run[0])
    guido.append(run[1])
    faffa.append(run[2])

# create plot
fig, ax = plt.subplots()
index = np.arange(n_groups)
fig.tight_layout()
fig.subplots_adjust(left=0.1, right=0.95)

bar_width = 0.2
opacity = 0.8

print index+bar_width 
rects1 = plt.bar(index, frank, bar_width,
                 alpha=opacity,
                 color='magenta',
                 label='#Elevelnodes=1000')
 
rects2 = plt.bar(index+bar_width, guido, bar_width,
                 alpha=opacity,
                 color='cyan',
                 label='#Elevelnodes=2000')

rects3 = plt.bar(index+bar_width+bar_width, faffa, bar_width,
                 alpha=opacity,
                 color='k',
                 label='#Elevelnodes=5000')
 
plt.xlabel('#PolicyIntents', fontsize=40)
plt.ylabel('Memory Utilization (GB)', fontsize=40)
plt.xticks(index + bar_width, ('1k', '2k', '3k', '4k', '5k', '6k', '7k', '8k', '9k', '10k', '11k', '12k', '13k', '14k', '15k', '16k'), rotation=45)
plt.legend(loc='upper left', fontsize=40)
plt.ylim([0, 3])
plt.show()
