from pyDatalog import pyDatalog
import json
import psutil
pyDatalog.create_terms('jointable, Nest_Cam, Network, Location, Floor, ID,L1,L2,L3,L4')



for i in range(10001):
    + Nest_Cam('NC'+str(i), 'LAN'+str(i//10))

for i in range(2001):
    + Floor('LAN'+str(i), 'Floor'+str(i//5))
    
for i in range(501):
    + Network('Floor'+str(i), 'Building'+str(i//3))
    
for j in range(251):
    + Location('Building'+str(j) , 'Campus'+str(j//2))
 
start = psutil.cpu_times()    
jointable(ID,L1,L2,L3,L4) <= Location(L1,ID) & Network(L2,L1) & Floor(L3,L2) & Nest_Cam(L4,L3)

    
Networks = {}
for i in jointable(ID,L1,L2,L3,L4):
    Networks[i[0]] = Networks.get(i[0] , {"Elevel": 2})
    Networks[i[0]][i[1]] = Networks[i[0]].get(i[1] , {})
    Networks[i[0]][i[1]][i[2]] = Networks[i[0]][i[1]].get(i[2] , {})
    Networks[i[0]][i[1]][i[2]][i[3]] = Networks[i[0]][i[1]][i[2]].get(i[3] , {})
    Networks[i[0]][i[1]][i[2]][i[3]][i[4]] = Networks[i[0]][i[1]][i[2]][i[3]].get(i[4] , {})
    Networks[i[0]][i[1]][i[2]][i[3]][i[4]] = i[4]
	
with open('netabs.json', 'w') as f:
    json.dump(Networks, f)

end = psutil.cpu_times()
print(end[0]-start[0])
#print(sum(end)-sum(start))