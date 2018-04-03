import numpy as np
import matplotlib.pyplot as plt
 
# data to plot
n_groups = 4
means_frank = [2390, 4340, 7560, 8925]
means_guido = [1870, 2890, 3540, 5340]
 
# create plot
fig, ax = plt.subplots()
index = np.arange(n_groups)
bar_width = 0.15
opacity = 0.6

print index+bar_width 
rects1 = plt.bar(index, means_frank, bar_width,
                 alpha=opacity,
                 color='b',
                 label='PGA')
 
rects2 = plt.bar(index+bar_width, means_guido, bar_width,
                 alpha=opacity,
                 color='g',
                 label='SecIntent')
 
plt.xlabel('#PolicyIntents', fontsize=16)
plt.ylabel('Latency (sec)', fontsize=16)
plt.xticks(index + bar_width, ('4000', '8000', '12000', '16000'))
plt.legend(loc='upper left', fontsize=16)
plt.tight_layout()
plt.savefig('comparion-pga-secintent.pdf')
