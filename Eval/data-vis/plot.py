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
E = [m2, ca2-22, cia2]
F = [m3, ca3-92, cia3]
X = np.arange(3)

width = 0.05

fig, ax = plt.subplots()
fig.tight_layout()
fig.subplots_adjust(left=0.1, right=0.95)

ax.bar(X, A, width, color='k', edgecolor='k', linewidth=6, log=True, label='PolicyList1(Manual)')
ax.bar(X+width+0.015, B, width, color='cyan', edgecolor='cyan', linewidth=6, log=True, label='PolicyList2(Manual)')
ax.bar(X+2*width+0.03, C, width, color='magenta', edgecolor='magenta', linewidth=6, log=True, label='PolicyList3(Manual)')
ax.bar(X+2*width+0.1, D, width, color='yellow', edgecolor='yellow', linewidth=6, log=True, label='PolicyGroup1(Abstraction)')
ax.bar(X+3*width+0.116, E, width, color='blue', edgecolor='blue', linewidth=6, log=True, label='PolicyGroup2(Abstraction)')
ax.bar(X+4*width+0.132, F, width, color='g', edgecolor='g', linewidth=6, log=True, label='PolicyGroup3(Abstraction)')
plt.ylabel('Number of Rules')
plt.xlabel('IoT Applications')
plt.xticks(np.arange(len(A))+3*width+0.015, ['Smart-Home', 'Smart-Campus', 'Smart-City'], fontsize=32)
plt.ylim([1, 10000000000])
plt.grid(linestyle='dotted')
plt.legend(ncol=2, fontsize=30, loc='upper left')
plt.show()
