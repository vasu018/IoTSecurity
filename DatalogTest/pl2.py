from pyDatalog import pyDatalog
import json
import psutil
pyDatalog.create_terms('jointable, Network, Location, ID,L1,L2')

for i in range(10001):
    + Network('LAN'+str(i), 'Building'+str(i//10))
    
for j in range(1000):
    + Location('Building'+str(j) , 'Campus'+str(j//10))
 
start = psutil.cpu_times()    
jointable(ID,L1,L2) <= Location(L1, ID) & Network(L2, L1)

    
Networks = {}
for i in jointable(ID,L1,L2):
    Networks[i[0]] = Networks.get(i[0] , {"Elevel": 2})
    Networks[i[0]][i[1]] = Networks[i[0]].get(i[1] , {})
    Networks[i[0]][i[1]][i[2]] = Networks[i[0]][i[1]].get(i[2] , {})
    Networks[i[0]][i[1]][i[2]] = i[2]
    
with open('absl2.json', 'w') as f:
    json.dump(Networks, f)

end = psutil.cpu_times()
print(end[0]-start[0])
#print(sum(end)-sum(start))