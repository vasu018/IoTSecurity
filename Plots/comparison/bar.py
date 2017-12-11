import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
 
# data to plot
n_groups = 4
means_frank = [2390, 4340, 7560, 8925]
means_guido = [1870, 2890, 3540, 4340]
 
# create plot
fig, ax = plt.subplots()
index = np.arange(n_groups)
bar_width = 0.15
opacity = 0.6

print index+bar_width 
rects1 = plt.bar(index, means_frank, bar_width,
                 alpha=opacity,
                 color='b',
                 label='Without Normalization')
 
rects2 = plt.bar(index+bar_width, means_guido, bar_width,
                 alpha=opacity,
                 color='g',
                 label='With Normalization (DynIntent)')
 
plt.xlabel('#PolicyIntents', fontsize=16)
plt.ylabel('Latency (sec)', fontsize=16)
plt.xticks(index + bar_width, ('4000', '8000', '12000', '16000'))
plt.legend(loc='upper left', fontsize=16)
plt.ylim([0,10000])
plt.tight_layout()
plt.grid(True)
plt.legend(loc = 'best', fontsize = 19)
plt.savefig("../Results/comparion-norm-dynintent.pdf", bbox_inches='tight')
plt.show()
