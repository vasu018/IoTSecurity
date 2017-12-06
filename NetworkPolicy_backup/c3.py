import re,json
from nested_lookup import nested_lookup
import networkx as nx

lowestlevels={}
G = nx.MultiDiGraph()
sideG = nx.MultiDiGraph()

def key_at_depth(dct, dpt):
    if dpt > 0:
        rlist=[]
        for k in dct:
            rlist+=key_at_depth(dct[k], dpt-1)
            
        return rlist
    else:
        return list(dct.keys())

def merge_list(llist,rlist):
    common=[]
    for i in llist:
        if i in rlist:
            common.append(i)
    if not common:
        return llist+rlist
    merged_list=[]
    lpos=0
    rpos=0
    for i in common:
        lindex = llist.index(i)
        rindex = rlist.index(i)
        if set(llist[lpos:lindex]).intersection(set(rlist[rpos:rindex])):
            return 
        merged_list += llist[lpos:lindex]
        merged_list += rlist[rpos:rindex]
        if i in merged_list:
            return
        merged_list.append(i)
        lpos = lindex+1
        rpos = rindex+1
    if lpos<len(llist):
        merged_list += llist[lpos:len(llist)]
    if rpos<len(rlist):
        merged_list += rlist[rpos:len(rlist)]
    return merged_list    

def is_conflicting(source,target):
    return source==target    
 
def add_edge(source,target,propdict,graphsource):
    for s in source:
        for t in target:
            if not graphsource.has_edge(s,t):
                graphsource.add_edges_from([(s,t,propdict)])
            else:
                for e in graphsource[s][t]:
                    scomp = is_conflicting(graphsource[s][t][e]['sourceprop'], propdict['sourceprop'])
                    tcomp = is_conflicting(graphsource[s][t][e]['targetprop'], propdict['targetprop'])
                    if scomp and tcomp:
                        if 'action' in graphsource[s][t][e] and (graphsource[s][t][e]['action']=='DENY'):
                            print("conflicting policy exist between",s," and ",t)
                        if 'route' in propdict and 'route' in graphsource[s][t][e]:
                            merged = merge_list(graphsource[s][t][e]['route'], propdict['route'])
                            if merged:
                                graphsource[s][t][e]['route']=merged
                        break
                           
def digestPolicies (policy_file):
    all_policies = [] 
    for pline in open(policy_file):
        policy_line = pline.strip()
        policy_line = re.sub('\s+', ' ', policy_line).strip()
        if not policy_line.startswith("#"):
            #print policy_line.rstrip()
            if not re.match(r'^\s+', pline):
                all_policies.append(policy_line)

    all_policies_dict = {}
    all_policies_dict = parsePolicies(all_policies)
    return all_policies_dict


#
# Parse the policies for extracting the policy attributes
#
def parsePolicies (policies_t):
    #print "# Policies for Parsing:\n", policies_t
    sfcs_t = []
    acls_t = []
    index = 1 
    for policy in policies_t:
        #print policy
        policy = re.sub('\s+', ' ', policy).strip()
        p_sfc = re.compile(r'>>')
        p_acl = re.compile(r'=>')
        if p_sfc.search(policy):
            # Debug Message for SFC Policy
            #print "#",index,". SFC Policy" 
            #print policy, "\n"
            sfcs_t.append(policy)
            index = index + 1 
        elif p_acl.search(policy):
            # Debug Message for ACL Policy
            #print "#",index,". Network ACL Policy" 
            #print policy, "\n"
            acls_t.append(policy)
            index = index + 1 
        else:
            print("# Invalid Policy Specified") 
            print(policy, "\n")

    sfcsDict = {}
    sfcsDict = sfcsToPythonDict (sfcs_t)
    aclsDict = {}
    aclsDict = aclsToPythonDict (acls_t)
    allPolicies_t = {}
    allPolicies_t['ACL'] = {}
    allPolicies_t['SFC'] = {}
    allPolicies_t['ACL'] = aclsDict['ACL']
    allPolicies_t['SFC'] = sfcsDict['SFC']
    return allPolicies_t
#
# SFCs list (Array) to Python Dictionary
#
def sfcsToPythonDict (sfcPolicies_t):

#     print("\n\n# SFC Policies to Python Dict ... ")
    policies_dict_t1 = {}
    policies_dict_t1['SFC'] = {}
    for index, policy in enumerate(sfcPolicies_t):
        # Debug messages for policy
        #print index+1, ":", policy
        policy = re.sub('\s+', ' ', policy).strip()
        policy_attributes = re.split(">>", policy)
        policies_dict_t1['SFC'][index+1] = {}
        for sub_index, attr in enumerate(policy_attributes):
            # Debug messages for policy attributes
            #print "\t", sub_index+1, ":", attr
            attr = re.sub('\s+', '', attr).strip()
            if (sub_index == 0):
                policies_dict_t1['SFC'][index+1]['source'] = attr
                #print attr
            elif (sub_index == len(policy_attributes) -1):
                policies_dict_t1['SFC'][index+1]['target'] = attr
                #print attr
            else:
                policies_dict_t1['SFC'][index+1][sub_index] = attr
    
    return policies_dict_t1        

#
# ACLs list (Array) to Python Dictionary
#
def aclsToPythonDict (aclPolicies_t):
    
#     print("# ACL Policies list to Python Dict ... ")
    policies_dict_t2 = {}
    policies_dict_t2['ACL'] = {}
    for index, policy in enumerate(aclPolicies_t):
        # Debug messages for policy
        #print index+1, ":", policy
        policies_dict_t2['ACL'][index+1] = {}
        policy = re.sub('\s+', ' ', policy).strip()
        policy_attributes = re.split("=>|!=>", policy)
        acl_type = re.compile(r'!=> | ! =>')
        if acl_type.search(policy):
            policies_dict_t2['ACL'][index+1]['action'] = "DENY"
        else:
            policies_dict_t2['ACL'][index+1]['action'] = "ALLOW"

        for sub_index, attr in enumerate(policy_attributes):
            attr = re.sub('\s+', '', attr).strip()
            if (sub_index == 0):
                policies_dict_t2['ACL'][index+1]['source'] = attr
                #print attr
            elif (sub_index == len(policy_attributes) -1):
                policies_dict_t2['ACL'][index+1]['target'] = attr
                #print attr
        
    return policies_dict_t2        
    
def convert_to_dict(policy):
    subparts = policy.split(".")
    retlist ={}
    for part in subparts:
        result = re.search('(.*){(.*)}',part)
        retlist[result.group(1)] = result.group(2) 
    return retlist

def set_min_level(policylist,abstractnet):
    alllevels={}
    #store all nodes for a location type
    for poltype in policylist:
        for pol in policylist[poltype]:
            sourcepart=convert_to_dict(policylist[poltype][pol]['source'])
            policylist[poltype][pol]['dictrep']={}
            policylist[poltype][pol]['dictrep']['source']=sourcepart
            targetpart=convert_to_dict(policylist[poltype][pol]['target'])
            policylist[poltype][pol]['dictrep']['target'] = targetpart
            
            commonparts = [i for i in sourcepart if i in abstractnet]
            
            c=commonparts[0]
            lowestlevels[c]=0
            levelspol = sourcepart[c].split(",")
            if c not in alllevels:
                alllevels[c] = set()
            alllevels[c].update(levelspol)
      
            commonparts = [i for i in targetpart if i in abstractnet]
            c=commonparts[0]
            lowestlevels[c]=0
            levelspol = targetpart[c].split(",")
            if c not in alllevels:
                alllevels[c] = set()
            alllevels[c].update(levelspol)
    
    #find min level for all location types
    for loctype in alllevels:                
        for levels in abstractnet[loctype]['Levels']:
            if not set(abstractnet[loctype]['Levels'][levels]).intersection(alllevels[loctype]):
                continue
            if lowestlevels[loctype] < int(levels):
                lowestlevels[loctype]=int(levels)
            if lowestlevels[loctype]>=abstractnet[loctype]['Elevel']:
                lowestlevels[loctype]=abstractnet[loctype]['Elevel']
                break
    
    
def compose_policy(policylist,abslevels):
    for poltype in policylist:
        for pol in policylist[poltype]:
            sourcenodes=[]
            sidesourcenodes=[]
            targetnodes=[]
            sidetargetnodes=[]
            edgeprop = {}
            edgeprop['sourceprop']={}
            edgeprop['targetprop']={} 
            if poltype == 'SFC':
                edgeprop['route']=[]
                for k in policylist[poltype][pol]:
                    if type(k)==type(0):
                        edgeprop['route'].append(policylist[poltype][pol][k])
            else:
                edgeprop['action']=policylist[poltype][pol]['action']
                
            for parts in policylist[poltype][pol]['dictrep']['source']:
                if parts in lowestlevels and not (sourcenodes or sidesourcenodes):
                    for level in abslevels[parts]["Levels"]:
                        currnodes = policylist[poltype][pol]['dictrep']['source'][parts].split(",")
                        common = set(abslevels[parts]["Levels"][level]).intersection(set(currnodes))
                        for node in common:
                            if lowestlevels[parts] == int(level):
                                sourcenodes.append(parts+"->"+node)
                            elif lowestlevels[parts] < int(level):
                                sidesourcenodes.append(parts+"->"+node)
                            else:
                                diff = lowestlevels[parts] - int(level)
                                cnodes=nested_lookup(node , abslevels[parts])[0]
                                childnodes = key_at_depth(cnodes, diff-1)
                                sourcenodes+=[parts+"->"+n for n in childnodes]       
                else:
                    edgeprop['sourceprop'][parts] = policylist[poltype][pol]['dictrep']['source'][parts]

            
            for parts in policylist[poltype][pol]['dictrep']['target']:
                if parts in lowestlevels and not (targetnodes or sidetargetnodes):
                    for level in abslevels[parts]["Levels"]:
                        currnodes = policylist[poltype][pol]['dictrep']['target'][parts].split(",")
                        common = set(abslevels[parts]["Levels"][level]).intersection(set(currnodes))
                        for node in common:
                            if lowestlevels[parts] == int(level):
                                targetnodes.append(parts+"->"+node)
                            elif lowestlevels[parts] < int(level):
                                sidetargetnodes.append(parts+"->"+node)
                            else:
                                diff = lowestlevels[parts] - int(level)
                                cnodes=nested_lookup(node , abslevels[parts])[0]
                                childnodes = key_at_depth(cnodes, diff-1)
                                targetnodes+=[parts+"->"+n for n in childnodes]             
                else:
                    edgeprop['targetprop'][parts] = policylist[poltype][pol]['dictrep']['target'][parts]
            
            if not (sourcenodes or targetnodes):
                add_edge(sidesourcenodes, sidetargetnodes,edgeprop,sideG)
                continue
            add_edge(sourcenodes, targetnodes,edgeprop,G)

                
if __name__ == "__main__":
    policylist = digestPolicies("policy.conf")
    abslevels = json.load(open("enterprise.json", "r"))
    set_min_level(policylist,abslevels)
    compose_policy(policylist,abslevels)
    for n in G.adjacency_iter():
        if n[1]:
            print(n)