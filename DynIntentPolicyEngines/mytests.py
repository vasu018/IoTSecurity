import networkx as nx
G = nx.MultiDiGraph()

G.add_edges_from([("LAN1{Enterprise-NW->LAN}","NET4{Enterprise-NW->DMZ}", {'sourceprop': {'parent': 'Enterprise-NW->LAN','abstype':'networks'}, 'targetprop': {'parent': 'Enterprise-NW->DMZ','abstype':'networks'}, 'action': 'DENY'})])
G.add_edges_from([("LAN1{Enterprise-NW->LAN}","NET5{Enterprise-NW->DMZ}", {'sourceprop': {'parent': 'Enterprise-NW->LAN','abstype':'networks'}, 'targetprop': {'parent': 'Enterprise-NW->DMZ','abstype':'networks'}, 'action': 'DENY'})])
G.add_edges_from([("LAN2{Enterprise-NW->LAN}","NET4{Enterprise-NW->DMZ}", {'sourceprop': {'parent': 'Enterprise-NW->LAN','abstype':'networks'}, 'targetprop': {'parent': 'Enterprise-NW->DMZ','abstype':'networks'}, 'action': 'DENY'})])
G.add_edges_from([("LAN2{Enterprise-NW->LAN}","NET5{Enterprise-NW->DMZ}", {'sourceprop': {'parent': 'Enterprise-NW->LAN','abstype':'networks'}, 'targetprop': {'parent': 'Enterprise-NW->DMZ','abstype':'networks'}, 'action': 'DENY'})])
G.add_edges_from([("W1{Application->Web}","D4{Application->DB}", {'sourceprop': {'parent': 'Application->Web','abstype':'applications','traffic-type':'Web,SocialNet','abstype':'applications'}, 'targetprop': {'parent': 'Enterprise-NW->DMZ','abstype':'applications'}, 'SFC': ['WEBFW','NF']})])
G.add_edges_from([("W1{Application->Web}","D4{Application->DB}", {'sourceprop': {'parent': 'Application->Web','abstype':'applications','traffic-type':'iot','abstype':'applications'}, 'targetprop': {'parent': 'Enterprise-NW->DMZ','abstype':'applications'}, 'SFC': ['DPI']})])
G.add_edges_from([("W1{Application->Web}","D4{Application->DB}", {'sourceprop': {'parent': 'Application->Web','abstype':'applications','traffic-type':'iot','abstype':'applications'}, 'targetprop': {'parent': 'Enterprise-NW->DMZ','abstype':'applications'}, 'SFC': ['DPI']})])
for n in G.adjacency_iter():
    if n[1]:
        print(n)