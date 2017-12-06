import json,random

def key_at_depth(dct, dpt):
    if dpt > 1:
        rlist={}
        for k in dct:
            if k=='Elevel':
                continue
            if isinstance(dct[k], dict):
                lower=key_at_depth(dct[k], dpt-1)
                for i in lower:
                    if lower[i]:
                        rlist[i]="%s->%s"%(k,lower[i])
                    else:
                        rlist[i]=k
            else:
                rlist[dct[k]] = ""
        return rlist
    else:
        temp = list(dct.keys())
        if 'Elevel' in temp:
            temp.remove('Elevel')
        return dict.fromkeys(temp)

def flattendir(mydir):
    policies = ""
    poltype = list(mydir.keys())
    midlayer = [" !=> "," => "," >> NF >> WF >> " , " >> WF >> DPI >> " , " >> DPI >> LB >> " ," >> LB >> WF >> "]
#     print(random.choice(midlayer))
    for _ in range(1000):
        sptype = random.choice(poltype)
        snodes = key_at_depth(mydir[sptype], random.randint(0,3))
        source = random.choice(list(snodes.keys()))
        sparent = snodes[source] if snodes[source] else ""
        tptype = random.choice(poltype)
        tnodes = key_at_depth(mydir[tptype], random.randint(0,3))
        target = random.choice(list(tnodes.keys()))
        tparent = tnodes[target] if tnodes[target] else ""
        policy = sptype+"{"+source+"}.parent{"+ sparent+"}"+ random.choice(midlayer) + tptype+"{"+target+"}.parent{"+ tparent+"}"
        policies += policy+"\n"
    return policies
        
        
def createstruct(filename):
    with open(filename,'r') as f:
        abstraction = json.load(f)
        
        with open('policies1/user1.conf','w') as f2:
            f2.write(flattendir(abstraction))
#         print(abstraction)
        
        
createstruct('abstractions/abs3.json')