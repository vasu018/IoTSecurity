from pyDatalog import pyDatalog
import json
import psutil
pyDatalog.create_terms('jointable, Nest_Cam, Network, Location, ID,L1,L2,L3')

for i in range(50001):
    + Nest_Cam('NC'+str(i), 'LAN'+str(i//10))
    
for i in range(5001):
    + Network('LAN'+str(i), 'Building'+str(i//10))
    
for j in range(501):
    + Location('Building'+str(j) , 'Campus'+str(j//10))
 
start = psutil.cpu_times()    
jointable(ID,L1,L2,L3) <= Nest_Cam(ID, L1) & Network(L1, L2) & Location(L2,L3)

    
Networks = {}
for i in jointable(ID,L1,L2,L3):
    Networks[i[3]] = Networks.get(i[3],{})
    Networks[i[3]][i[2]] = Networks[i[3]].get(i[2] , {})
    Networks[i[3]][i[2]][i[1]] = Networks[i[3]][i[2]].get(i[1] , {})
    Networks[i[3]][i[2]][i[1]][i[0]] = i[0]
    
with open('netabs.json', 'w') as f:
    json.dump(Networks, f)

end = psutil.cpu_times()
print(end[0]-start[0])
#print(sum(end)-sum(start))