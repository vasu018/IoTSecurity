import os
import numpy as np
import matplotlib.pyplot as plt

depths = [1, 2, 3, 4, 5]

data = {}
d = np.loadtxt('data.txt')
for run in d:
    data.setdefault(1, []).append(run[0])
    data.setdefault(2, []).append(run[1])
    data.setdefault(3, []).append(run[2])
    data.setdefault(4, []).append(run[3])
    data.setdefault(5, []).append(run[4])

f = plt.figure()
def cdf(data, Colour, Label):
    global f
    data_size=len(data)

    data_set=sorted(set(data))
    bins=np.append(data_set, data_set[-1]+1)

    # Use the histogram function to bin the data
    counts, bin_edges = np.histogram(data, bins=bins, density=False)

    counts=counts.astype(float)/data_size

    # Find the cdf
    cdf = np.cumsum(counts)

    # Plot the cdf
    plt.plot(bin_edges[0:-1], cdf,linestyle='-', linewidth=3, color=Colour, label=Label)
cdf(data[1], 'r', 'depth=1')
cdf(data[2], 'g', 'depth=2')
cdf(data[3], 'b', 'depth=3')
cdf(data[4], 'm', 'depth=4')
cdf(data[5], 'k', 'depth=5')
plt.ylim((0,1))
plt.xlim((0,900))
plt.ylabel("CDF")
plt.xlabel("Latency (ms)")
plt.legend(loc='lower right', numpoints=1)
f.savefig("depth-latency.pdf")
