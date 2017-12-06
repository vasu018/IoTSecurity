from pyDatalog import pyDatalog
import json
import psutil
pyDatalog.create_terms('jointable, S1,S2,S3,S4,S5,S6,S7,L1,L2,L3,L4,L5,L6,L7,L8')

for i in range(5):
    + S1('D1_'+str(i//4), 'D2_'+str(i))

for i in range(20):
    + S2('D2_'+str(i//2), 'D3_'+str(i))
	
for i in range(50):
    + S3('D3_'+str(i//2), 'D4_'+str(i))

for i in range(101):
    + S4('D4_'+str(i//2), 'D5_'+str(i))
	
for i in range(251):
    + S5('D5_'+str(i//2), 'D6_'+str(i))

for i in range(1001):
    + S6('D6_'+str(i//2), 'D7_'+str(i))
	
for i in range(10001):
    + S7('D7_'+str(i//5), 'D8_'+str(i))

 
start = psutil.cpu_times()    
jointable(L1,L2,L3,L4,L5,L6,L7,L8) <= S1(L1,L2) & S2(L2,L3) & S3(L3,L4) & S4(L4,L5) & S5(L5,L6) & S6(L6,L7) & S7(L7,L8)

    
Networks = {}
for i in jointable(L1,L2,L3,L4,L5,L6,L7,L8):
    Networks[i[0]] = Networks.get(i[0] , {"Elevel": 2})
    Networks[i[0]][i[1]] = Networks[i[0]].get(i[1] , {})
    Networks[i[0]][i[1]][i[2]] = Networks[i[0]][i[1]].get(i[2] , {})
    Networks[i[0]][i[1]][i[2]][i[3]] = Networks[i[0]][i[1]][i[2]].get(i[3] , {})
    Networks[i[0]][i[1]][i[2]][i[3]][i[4]] = Networks[i[0]][i[1]][i[2]][i[3]].get(i[4] , {})
    Networks[i[0]][i[1]][i[2]][i[3]][i[4]][i[5]] = Networks[i[0]][i[1]][i[2]][i[3]][i[4]].get(i[5] , {})
    Networks[i[0]][i[1]][i[2]][i[3]][i[4]][i[5]][i[6]] = Networks[i[0]][i[1]][i[2]][i[3]][i[4]][i[5]].get(i[6] , {})
    Networks[i[0]][i[1]][i[2]][i[3]][i[4]][i[5]][i[6]][i[7]] = Networks[i[0]][i[1]][i[2]][i[3]][i[4]][i[5]][i[6]].get(i[7] , {})
    Networks[i[0]][i[1]][i[2]][i[3]][i[4]][i[5]][i[6]][i[7]]  = i[7]
	
with open('abs100.json', 'w') as f:
    json.dump(Networks, f)

end = psutil.cpu_times()
print(end[0]-start[0])
#print(sum(end)-sum(start))