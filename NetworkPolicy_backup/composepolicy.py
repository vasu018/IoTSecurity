'''
Created on Jan 4, 2017

@author: Mahendra
'''
import networkx as nx
G = nx.MultiDiGraph()
#G.add_nodes_from(['LAN2','Internet','AdminNet','WEBFW','NF','lB'])
# G.add_edges_from([(('LAN1','LAN2'),'DMZ',{"perm":"NA"})])
G.add_edge('LAN1','DMZ',"perm",{"NA":1})
G.add_edge('LAN1','DMZ',"perm",{"NA":1})
# G.add_edges_from([('LAN2','DMZ',{"perm":"NA"})])
# G.add_edges_from([('DMZ','Internet',{"route":["WebFW",],"traffic-type":"Web,social"})])
# G.add_edges_from([('DMZ','Internet',{"perm":"NA"})])
# G.add_node(1)
# G.add_nodes_from({1:5,2:4,3:6})
# G.add_edges_from([(4,5,dict(route=282))])
# G.add_edges_from([(4,5,dict(route=296))])
# G.add_nodes_from(range(100,110))
#G.add_edges_from([(4,5,dict(route=282)), (4,5,dict(route=37))])
for n in G.adjacency_iter():
    print(n)
# H=nx.Graph()
# H.add_path([0,1,2,3,4,5,6,7,8,9])
# G.add_nodes_from(H)

