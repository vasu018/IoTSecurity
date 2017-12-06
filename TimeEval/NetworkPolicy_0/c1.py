import re,json
from nested_lookup import nested_lookup
import networkx as nx
import matplotlib
G = nx.MultiDiGraph()
sideG = nx.MultiDiGraph()
# Digest the policy file for extracting the actives rules
#

def add_edge(source,target,keyprop,propdict):
    if G.has_edge(source,target):
        edata=G[source][target]
        if ('perm' in edata) and edata['perm']['allowed']=='DENY':
            print("conflicting policy found. Ignoring!!!")
            return
    G.add_edge(source,target,keyprop,propdict)
 
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

policylist=digestPolicies("policy.conf")
abslevels=json.load(open("enterprise.json", "r"))
minlevels={}
for poltype in policylist:
    for pol in policylist[poltype]:
        sourcep=policylist[poltype][pol]['source']
        sourceparts = sourcep.split(".")
        for p in sourceparts:
            if 'networks' in p:
                result =  re.search('networks{(.*)}',p)
                level_spec=result.group(1).split(",")[0]
#                 print(level_spec)
                for levels in abslevels['Levels']:
                    if level_spec in abslevels['Levels'][levels]:
                        if ('networks' in minlevels) and minlevels['networks'] < int(levels):
                            minlevels['networks']=int(levels)
                            if minlevels['networks']>=abslevels['networks']['Elevel']['level']:
                                minlevels['networks']=abslevels['networks']['Elevel']['level']
                                break
                        elif ('networks' not in minlevels):
                            minlevels['networks']=int(levels)
                            if minlevels['networks']>=abslevels['networks']['Elevel']['level']:
                                minlevels['networks']=abslevels['networks']['Elevel']['level']
                                break
                            
            elif 'applications' in p:
                result =  re.search('applications{(.*)}',p)
                level_spec=result.group(1).split(",")[0]
#                 print(level_spec)
                for levels in abslevels['Levels']:
                    if level_spec in abslevels['Levels'][levels]:
                        if ('applications' in minlevels) and minlevels['applications'] < int(levels):
                            minlevels['applications']=int(levels)
                            if minlevels['applications']>=abslevels['applications']['Elevel']['level']:
                                minlevels['applications']=abslevels['applications']['Elevel']['level']
                                break
                        elif ('applications' not in minlevels):
                            minlevels['applications']=int(levels)
                            if minlevels['applications']>=abslevels['applications']['Elevel']['level']:
                                minlevels['applications']=abslevels['applications']['Elevel']['level']
                                break
            else:
                continue
# print(policylist)

# def compose_policies(policies):
for poltype in policylist:
    for pol in policylist[poltype]:
        perm=None
        sourcep=policylist[poltype][pol]['source']
        targetp=policylist[poltype][pol]['target']
        targetparts = targetp.split(".")
        targetnodes=[]
        for p in targetparts:
            if 'networks' in p:
                result =  re.search('networks{(.*)}',p)
                level_spec=result.group(1).split(",")[0]
                targetnodes.append(level_spec)
            elif 'applications' in p:
                result =  re.search('applications{(.*)}',p)
                level_spec=result.group(1).split(",")[0]
                targetnodes.append(level_spec)
        sourceparts = sourcep.split(".")
        for p in sourceparts:
            if 'networks' in p:
                result =  re.search('networks{(.*)}',p)
                sources=result.group(1).split(",")
                for level_spec in sources:
                    for levels in abslevels['Levels']:
                        if level_spec in abslevels['Levels'][levels]:
                            if minlevels['networks'] > int(levels):
                                childnodes=nested_lookup(level_spec , abslevels['networks'])[0]
                                for n in childnodes:
                                    if poltype == 'SFC':
                                        for k in policylist[poltype][pol]:
                                            if type(k)==type(0):
                                                add_edge(n, targetnodes[0],"route",{k:policylist[poltype][pol][k]})
                                    else:
                                        add_edge(n, targetnodes[0],"perm",{"allowed":policylist[poltype][pol]['action']})
                            elif minlevels['networks'] == int(levels):
                                if poltype == 'SFC':
                                    for k in policylist[poltype][pol]:
                                        if type(k)==type(0):
                                            add_edge(level_spec, targetnodes[0],"route",{k:policylist[poltype][pol][k]})
                                else:
                                    add_edge(level_spec, targetnodes[0],"perm",{"allowed":policylist[poltype][pol]['action']})
                            else:
                                if poltype == 'SFC':
                                        for k in policylist[poltype][pol]:
                                            if type(k)==type(0):
                                                add_edge(level_spec, targetnodes[0],"route",{k:policylist[poltype][pol][k]})
                                else:
                                    add_edge(level_spec, targetnodes[0],"perm",{"allowed":policylist[poltype][pol]['action']})
                            break
            if 'applications' in p:
                result =  re.search('applications{(.*)}',p)
                sources=result.group(1).split(",")
                for level_spec in sources:
                    for levels in abslevels['Levels']:
                        if level_spec in abslevels['Levels'][levels]:
                            if minlevels['applications'] > int(levels):
                                childnodes=nested_lookup(level_spec , abslevels['applications'])[0]
                                for n in childnodes:
                                    if poltype == 'SFC':
                                        for k in policylist[poltype][pol]:
                                            if type(k)==type(0):
                                                add_edge(n, targetnodes[0],"route",{k:policylist[poltype][pol][k]})
                                    else:
                                        add_edge(n, targetnodes[0],"perm",{"allowed":policylist[poltype][pol]['action']})
                            elif minlevels['applications'] == int(levels):
                                if poltype == 'SFC':
                                        for k in policylist[poltype][pol]:
                                            if type(k)==type(0):
                                                add_edge(level_spec, targetnodes[0],"route",{k:policylist[poltype][pol][k]})
                                else:
                                    add_edge(level_spec, targetnodes[0],"perm",{"allowed":policylist[poltype][pol]['action']})
                            else:
                                if poltype == 'SFC':
                                        for k in policylist[poltype][pol]:
                                            if type(k)==type(0):
                                                add_edge(level_spec, targetnodes[0],"route",{k:policylist[poltype][pol][k]})
                                else:
                                    add_edge(level_spec, targetnodes[0],"perm",{"allowed":policylist[poltype][pol]['action']})
                            break

# print(G.edges(keys=True))
       
for n in G.adjacency_iter():
    if n[1]:
        print(n)
        
        
draw(G)