import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size':45})

# data to plot
n_groups = 16
frank = [4.2, 4.9, 5.5, 7.3, 8.7, 9.5, 12.2, 13.7, 15.4, 17.3, 19.4, 21.2, 23, 24.3, 25.5, 26]
guido = [5.1, 6.2, 7, 8.4, 10.2, 11.3, 13.4, 15.7, 16.7, 18.9, 20, 22.3, 24.3, 26, 27, 28]
faffa = [8.6, 9.1, 10.8, 12.5, 13.1, 14.2, 16.1, 17.2, 19.1, 21, 23, 25.2, 27, 29.2, 30, 31] 
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
plt.ylabel('CPU Utilization (%)', fontsize=40)
plt.xticks(index + bar_width, ('1k', '2k', '3k', '4k', '5k', '6k', '7k', '8k', '9k', '10k', '11k', '12k', '13k', '14k', '15k', '16k'), rotation=45)
plt.legend(loc='upper left', fontsize=40)
plt.ylim([0,58])
plt.show()
