from c4 import *
import sys
from timeit import default_timer as timer
def get_nnodes(n,parent,poltype,translations):
    pass

def get_network(node):
    if node in nn:
        net = nn[node]
    else:
        i = re.search('(.*){(.*)}',node)
        net = "->".join([i.group(2),i.group(1)]) if i.group(2) else i.group(1)
    if net in ipmap:
        if node in poltypes and (poltypes[node] in ipmap[net]):
            return ipmap[net][poltypes[node]]
        elif node in poltypes:
            return ipmap[net]['networks']
        else:
            return ""    
    else:
        print("No mapping found for "+net)
        return ""
        
if __name__ == "__main__":
    starttime = timer()
    Graphs = create_graphs()
    translations = json.load(open("Translate.json", "r"))
    comp = nx.MultiDiGraph()
    for g in Graphs:
        user1_graph = Graphs[g]['main']
        mappings= {}
        #parents = c4.nx.get_node_attributes(user1_graph,"parent")
        poltypes = nx.get_node_attributes(user1_graph,"polabstract")
        netnodes = []
        for n in user1_graph:
            if poltypes[n]=='networks':
                netnodes.append(n)
                continue
            elif poltypes[n]=='Hosts':
                continue
            mappings[n] = translations[n] if n in translations else 'default'
        nx.set_node_attributes(user1_graph,"network",mappings)
    
        nn = nx.get_node_attributes(user1_graph,"network")
        for nodes in nn:
            for networknodes in netnodes:
                i = re.search('(.*){(.*)}',networknodes)
                loc1 = "->".join([i.group(2),i.group(1)]) if i.group(2) else i.group(1)
                if nn[nodes].startswith(loc1):
                    for dest in user1_graph[networknodes]:
                        for e in user1_graph[networknodes][dest]:
                            add_edge([nodes], [dest], user1_graph[networknodes][dest][e], user1_graph,True)
                
        comp = nx.compose(comp, user1_graph)
     
#     print("\nFollowing is the composed graph:")
#     for n in comp.adjacency_iter():
#         if n[1]:
#             print(n)

    composenetnodes = []
    poltypes = nx.get_node_attributes(comp,"polabstract")
    for n in comp:
        if n in poltypes and poltypes[n]=='networks':
            composenetnodes.append(n)
            
    nn = nx.get_node_attributes(comp,"network")
#     print("\nPrinting network of other abstraction:")
#     print(nn)
    for nodes in nn:
        for networknodes in composenetnodes:
            i = re.search('(.*){(.*)}',networknodes)
            loc1 = "->".join([i.group(2),i.group(1)]) if i.group(2) else i.group(1)
            if nn[nodes].startswith(loc1):
                for dest in comp[networknodes]:
                    for e in comp[networknodes][dest]:
                        add_edge([nodes], [dest], comp[networknodes][dest][e], comp,True)
        

    print(timer()-starttime)
    sys.exit(0)
    finalgraph = nx.MultiDiGraph()
    ipmap = json.load(open("ipmapping.json", "r"))
    for n in comp:
        for dest in comp[n]:
            s = get_network(n)
            t = get_network(dest)
            for e in comp[n][dest]:
                add_edge([s],[t],comp[n][dest][e],finalgraph)
            
#     print("\nFinal Graph after mapping:")
#     for n in finalgraph.adjacency_iter():
#         if n[1]:
#             print(n)
        
    print(timer()-starttime)