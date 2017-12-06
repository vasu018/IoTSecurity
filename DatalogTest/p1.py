from pyDatalog import pyDatalog
from timeit import default_timer as timer
import json
pyDatalog.create_terms('jointable, Nest_Cam, Location, ID,L1,L2')
#s = 'Nest_Cams(Nest_Cam{0},NC{1},Building{2}).'
# + Nest_Cam('NC1','B1')
# + Location('B1','C1')

for i in range(501):
    + Nest_Cam('NC '+str(i), 'Building '+str(i//10))
 
for j in range(51):
    + Location('Building '+str(j) , 'Campus '+str(j//10))
   
start = timer() 
jointable(ID,L1,L2) <= Nest_Cam(ID,L1) & Location(L1,L2) 

# print(timer()-start)
#print(jointable(ID,L1,L2))
Vendors = {}
for i in jointable(ID,L1,L2):
    Vendors[i[2]] = Vendors.get(i[2],{})
    Vendors[i[2]][i[1]] = Vendors[i[2]].get(i[1] , {})
    Vendors[i[2]][i[1]][i[0]] = i[0]
    
# print(Vendors)
# save to file:
with open('abs.json', 'w') as f:
    json.dump(Vendors, f)

print(timer()-start)