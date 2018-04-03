import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
matplotlib.rcParams.update({'font.size':36})

lines = open('smart-home/smart-home.csv', 'r')
devices = []
abss = []
for line in lines:
	line = line.split(',')
	abss.append(line[0])
	device = line[0].split(':')
	devices.append(device[1])

devices = Counter(devices)

p1 = 0
p2 = 0
p3 = 0
for i in devices:
	if 'light' in i:
		p1 += devices[i]
	if 'closet' in i:
		p2 += devices[i]
	if 'fan' in i:
		p3 += devices[i]
print p1, p2, p3

abss = Counter(abss)
m1 = 0
m2 = 0
m3 = 0

for i in abss:
	if 'lights' in i:
		m1 += 1
	if 'closet' in i:
		m2 += 1
	if 'fan' in i:
		m3 += 1
print m1, m2, m3

lines = open('smart-campus/smart-campus.csv', 'r')
devices = []
abss = []
for line in lines:
        line = line.split(' ')
        devices.append(line[3])
        abss.append(line[2]+':'+line[3])
devices = Counter(devices)
abss = Counter(abss)
c1 = 0
c2 = 0
c3 = 0
ca1 = 0
ca2 = 0
ca3 = 0
for i in devices:
	if 'Motion' in i:
		c1 += devices[i]
	if 'Sensor' in i:
		c2 += devices[i]
	if 'Battery' in i:
		c3 += devices[i]

for i in abss:
	if 'Motion' and 'C0':
		ca1 += 1
	if 'Sensor' and 'C0':
		ca2 += 1
	if 'Battery' and 'C0':
		ca3 += 1

ci1 = 10032569
ci2 = 5936100
ci3 = 3032400

cia1 = 18623
cia2 = 13234
cia3 = 10024

A = [p1, c1, ci1]
B = [p2, c2, ci2]
C = [p3, c3, ci3]
D = [m1, ca1, cia1]
E = [m2, ca2, cia2]
F = [m3, ca3, cia3]
X = np.arange(3)

width = 0.2

fig, ax = plt.subplots()
fig.tight_layout()
fig.subplots_adjust(left=0.1, right=0.95)

ax.bar(X, A, width, color='magenta', edgecolor='magenta', linewidth=6, log=True, label='Manual-Policy1')
ax.bar(X, B, width, bottom = A, color='blue', edgecolor='blue', linewidth=6, log=True, label='Manual-Policy2')
ax.bar(X, C, width, bottom = np.array(A)+np.array(B), color='orange', edgecolor='orange', linewidth=6, log=True, label='Manual-Policy3')
#ax.bar(X+1.2*width, D, width, color='yellow', edgecolor='yellow', linewidth=6, log=True, label='Abstraction-Policy1')
#ax.bar(X+1.2*width, E, width, bottom = D, color='cyan', edgecolor='cyan', linewidth=6, log=True, label='Abstraction-Policy2')
#ax.bar(X+1.2*width, F, width, bottom = np.array(D)+np.array(E), color='k', edgecolor='k', linewidth=6, log=True, label='Abstraction-Policy3')
plt.ylabel('Number of Nodes')
plt.xlabel('IoT Environs')
plt.xticks(np.arange(len(A))+0.6*width, ['Smart-Home', 'Smart-Campus', 'Smart-City'], fontsize=28)
plt.ylim([1, 10000000000])
plt.grid(linestyle='dotted')
plt.legend(ncol=3, fontsize=26)
plt.show()
