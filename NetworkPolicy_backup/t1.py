import c4,json,re

# def get_nnodes(n,parent,poltype,translations):
#     if poltype=='networks':
#         return ""
#     if poltype not in translations:
#         print("Invalid policy type %s"%poltype)
#         return ""
#     location = translations[poltype]
#     if 'network' in location:
#         return location['network']
#     parts = parent.split("->")
#     for i in parts:
#         if i not in location:
#             print("Invalid policy path %s"%i)
#             return ""
#         location = location[i]
#         if 'network' in location:
#             return location['network']
#     return location['network']

def get_nnodes(n,parent,poltype,translations):
    pass

if __name__ == "__main__":
    policylist = c4.digestPolicies("policies/user1.conf")
    abstractions = json.load(open("abstractions/user1.json", "r"))
    translations = json.load(open("Translate.json", "r"))
    c4.set_min_level(policylist,abstractions)
    c4.compose_policy(policylist,abstractions)
    user1_graph = c4.G
    mappings= {}
#     parents = c4.nx.get_node_attributes(user1_graph,"parent")
    poltypes = c4.nx.get_node_attributes(user1_graph,"polabstract")
    netnodes = []
    for n in user1_graph:
        if poltypes[n]=='networks':
            netnodes.append(n)
            continue
        mappings[n] = translations[n]#get_nnodes(n,parents[n],poltypes[n],translations)
    c4.nx.set_node_attributes(user1_graph,"network",mappings)

    nn = c4.nx.get_node_attributes(user1_graph,"network")
    for nodes in nn:
        for networknodes in netnodes:
            i = re.search('(.*){(.*)}',networknodes)
            loc1 = "->".join([i.group(2),i.group(1)]) if i.group(2) else i.group(1)
            if loc1.startswith(nn[nodes]):
                for dest in user1_graph[networknodes]:
                    for e in user1_graph[networknodes][dest]:
                        c4.add_edge([nodes], [dest], user1_graph[networknodes][dest][e], user1_graph)
    

    for n in user1_graph.adjacency_iter():
        if n[1]:
            print(n)