import re,json
import networkx as nx


lowestlevels={}
G = nx.MultiDiGraph()
sideG = nx.MultiDiGraph()

def is_conflicting(source,target):
    return source==target   

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

def add_edge(source,target,propdict,graphsource):
    for s in source:
        for t in target:
            if not graphsource.has_edge(s,t):
                graphsource.add_edges_from([(s,t,propdict)])
                sp = re.search('(.*){(.*)}',s)
                tp = re.search('(.*){(.*)}',t)
                nx.set_node_attributes(graphsource,"parent",{s:sp.group(2),t:tp.group(2)})
                nx.set_node_attributes(graphsource,"polabstract",{s:propdict['sourceprop']['polabstract'],t:propdict['targetprop']['polabstract']})
            else:
                isadded = False
                for e in graphsource[s][t]:
                    scomp = is_conflicting(graphsource[s][t][e]['sourceprop'], propdict['sourceprop'])
                    tcomp = is_conflicting(graphsource[s][t][e]['targetprop'], propdict['targetprop'])
                    if scomp and tcomp:
                        if 'action' in graphsource[s][t][e] and (graphsource[s][t][e]['action']=='DENY'):
                            print("conflicting policy exist between",s," and ",t)
                            isadded = True
                        if 'SFC' in propdict and 'SFC' in graphsource[s][t][e]:
                            merged = merge_list(graphsource[s][t][e]['SFC'], propdict['SFC'])
                            if merged:
                                graphsource[s][t][e]['SFC']=merged
                            else:
                                print("conflicting SFC exist between",s," and ",t)
                            isadded = True
                        break
                if not isadded:
                    graphsource.add_edges_from([(s,t,propdict)])
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

def convert_to_dict(policy):
    subparts = policy.split(".")
    retlist ={}
    for part in subparts:
        result = re.search('(.*){(.*)}',part)
        retlist[result.group(1)] = result.group(2) 
    return retlist

def digestPolicies (policy_file):
    all_policies = [] 
    for pline in open(policy_file):
        policy_line = pline.strip()
        policy_line = re.sub('\s+', ' ', policy_line).strip()
        if not policy_line.startswith("#"):
            #print policy_line.rstrip()
            if not re.match(r'^\s+', pline):
                all_policies.append(policy_line)

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

    sfcsDict = sfcsToPythonDict (sfcs_t)
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

def set_min_level(policylist,abstract):
    for poltype in policylist:
        for pol in policylist[poltype]:
            sourcepart=convert_to_dict(policylist[poltype][pol]['source'])
            policylist[poltype][pol]['dictrep']={}
            policylist[poltype][pol]['dictrep']['source']=sourcepart
            targetpart=convert_to_dict(policylist[poltype][pol]['target'])
            policylist[poltype][pol]['dictrep']['target'] = targetpart
            
#             if not verify_policy(sourcepart, targetpart, abstract):
#                 print("Invalid policy: ",end="")
#                 print(policylist[poltype][pol])
#                 policylist[poltype][pol]=""
#                 continue
            
            sourcepath = sourcepart['parent'].split("->")
            sourcepath = list(filter(None, sourcepath))
            sourcepol_abstract = list(set(sourcepart) & set(abstract))[0]
            sourcepart['polabstract']=sourcepol_abstract
            if not sourcepol_abstract in lowestlevels:
                lowestlevels[sourcepol_abstract]={}
            if sourcepath and sourcepath[0] not in lowestlevels[sourcepol_abstract]:
                lowestlevels[sourcepol_abstract][sourcepath[0]]=min(len(sourcepath),abstract[sourcepol_abstract][sourcepath[0]]['Elevel'])
            elif sourcepath and (lowestlevels[sourcepol_abstract][sourcepath[0]] < len(sourcepath) <= abstract[sourcepol_abstract][sourcepath[0]]['Elevel']):
                lowestlevels[sourcepol_abstract][sourcepath[0]] = len(sourcepath)
            elif (not sourcepath) and (policylist[poltype][pol]['dictrep']['source'][sourcepol_abstract] not in lowestlevels[sourcepol_abstract]):
                lowestlevels[sourcepol_abstract][policylist[poltype][pol]['dictrep']['source'][sourcepol_abstract]]=0
                
            targetpath = targetpart['parent'].split("->")
            targetpath = list(filter(None, targetpath))
            targetpol_abstract = list(set(targetpart) & set(abstract))[0]
            targetpart['polabstract']=targetpol_abstract
            if not targetpol_abstract in lowestlevels:
                lowestlevels[targetpol_abstract]={}
            if targetpath and targetpath[0] not in lowestlevels[targetpol_abstract]:
                lowestlevels[targetpol_abstract][targetpath[0]] = min(len(targetpath),abstract[targetpol_abstract][targetpath[0]]['Elevel'])
            elif targetpath and (lowestlevels[targetpol_abstract][targetpath[0]] < len(targetpath) <= abstract[targetpol_abstract][targetpath[0]]['Elevel']):
                lowestlevels[targetpol_abstract][targetpath[0]] = len(targetpath)
            elif (not targetpath) and (policylist[poltype][pol]['dictrep']['target'][targetpol_abstract] not in lowestlevels[targetpol_abstract]):
                lowestlevels[targetpol_abstract][policylist[poltype][pol]['dictrep']['target'][targetpol_abstract]]=0
       
def compose_policy(policylist,abslevels):
    for poltype in policylist:                                  # poltype here means SFC or ACL
        for pol in policylist[poltype]:
            if not policylist[poltype][pol]:
                continue
            pdict = policylist[poltype][pol]['dictrep']         # dict containing source and destination fields
            sourcenodes=[]
            sidesourcenodes=[]
            spoltype = pdict['source']['polabstract']           # networks, application etc (top level in abstractions)
            spoltarget = pdict['source'][spoltype]              # source nodes candidates LAN1, LAN2 etc    
            targetnodes=[]
            sidetargetnodes=[]
            tpoltype = pdict['target']['polabstract']           # networks, application etc (top level in abstractions)
            tpoltarget = pdict['target'][tpoltype]              # source nodes candidates LAN1, LAN2 etc    
            edgeprop = {}
            edgeprop['sourceprop']={}
            edgeprop['targetprop']={}
            
            if poltype == 'SFC':
                edgeprop['SFC']=[]
                for k in policylist[poltype][pol]:
                    if type(k)==type(0):
                        edgeprop['SFC'].append(policylist[poltype][pol][k])
            else:
                edgeprop['action']=policylist[poltype][pol]['action']
            
            sparent = pdict['source']['parent'].split("->")
            sparent = list(filter(None, sparent))
            if (sparent and len(sparent) == lowestlevels[spoltype][sparent[0]] or 
                ((spoltarget in lowestlevels[spoltype]) and lowestlevels[spoltype][spoltarget]==0)):
                sourcenodes+=["%s{%s}"%(i,pdict['source']['parent']) for i in spoltarget.split(",")]
            elif sparent and len(sparent) > lowestlevels[spoltype][sparent[0]]:
                sidesourcenodes+=["%s{%s}"%(i,pdict['source']['parent']) for i in spoltarget.split(",")]
            else:
                if not sparent:
                    diff = lowestlevels[spoltype][spoltarget]
                    location = abslevels[spoltype]
                else:
                    diff = lowestlevels[spoltype][sparent[0]] - len(sparent)
                    location = abslevels[spoltype][sparent[0]]
                    for i in sparent[1:]:
                        location = location[i]
                for i in spoltarget.split(","):
                    childnodes = key_at_depth(location[i], diff)    
                    for n in childnodes:
                        if childnodes[n]:
                            if sparent:
                                childnodes[n] = "%s->%s->%s"%(pdict['source']['parent'],i,childnodes[n])
                            else:
                                childnodes[n] = "%s->%s"%(i,childnodes[n]) 
                        else:
                            if sparent:
                                childnodes[n] = "%s->%s"%(pdict['source']['parent'],i)
                            else:
                                childnodes[n] = i 
                        sourcenodes+=["%s{%s}"%(n,childnodes[n])]
                        
                        
        
            tparent = pdict['target']['parent'].split("->")
            tparent = list(filter(None, tparent))
            if (tparent and len(tparent) == lowestlevels[tpoltype][tparent[0]] or 
                ((tpoltarget in lowestlevels[tpoltype]) and lowestlevels[tpoltype][tpoltarget]==0)):
                targetnodes+=["%s{%s}"%(i,pdict['target']['parent']) for i in tpoltarget.split(",")]
            elif tparent and len(tparent) > lowestlevels[tpoltype][tparent[0]]:
                sidetargetnodes+=["%s{%s}"%(i,pdict['target']['parent']) for i in tpoltarget.split(",")]
            else:
                if not tparent:
                    diff = lowestlevels[tpoltype][tpoltarget]
                    location = abslevels[tpoltype]
                else:
                    diff = lowestlevels[tpoltype][tparent[0]] - len(tparent)
                    location = abslevels[tpoltype][tparent[0]]
                    for i in tparent[1:]:
                        location = location[i]
                for i in tpoltarget.split(","):
                    if i not in location:
                        print("Invalid location,%s",i)
                        continue
                    childnodes = key_at_depth(location[i], diff)    
                    for n in childnodes:
                        if childnodes[n]:
                            if tparent:
                                childnodes[n] = "%s->%s->%s"%(pdict['target']['parent'],i,childnodes[n])
                            else:
                                childnodes[n] = "%s->%s"%(i,childnodes[n]) 
                        else:
                            if sparent:
                                childnodes[n] = "%s->%s"%(pdict['target']['parent'],i)
                            else:
                                childnodes[n] = i 
                        targetnodes+=["%s{%s}"%(n,childnodes[n])]
             
            for prop in pdict['source']:
                if prop==pdict['source']['polabstract'] or prop == 'parent':
                    continue
                edgeprop['sourceprop'][prop]=pdict['source'][prop]
                
            for prop in pdict['target']:
                if prop==pdict['target']['polabstract'] or prop == 'parent':
                    continue
                edgeprop['targetprop'][prop]=pdict['target'][prop]
                
            if not (sourcenodes or targetnodes):
                add_edge(sidesourcenodes, sidetargetnodes,edgeprop,sideG)
                continue
            add_edge(sourcenodes, targetnodes,edgeprop,G)
            
if __name__ == "__main__":
    policylist = digestPolicies("policies/user1.conf")
    abstractions = json.load(open("abstractions/user1.json", "r"))
    set_min_level(policylist,abstractions)
    compose_policy(policylist,abstractions)
    for n in G.adjacency_iter():
        if n[1]:
            print(n)