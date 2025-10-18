import networkx as nx

from Func import *


G = nx.erdos_renyi_graph(n=15, p=0.1, directed=True)
activation_probability = 0.2
T = 20
Select = list(sorted(G.nodes()))


for i in range(2):
    P = [G.degree(u) for u in sorted(G.nodes())]
    P = [val / sum(P) for val in P]

    S = np.random.choice(a=list(sorted(G.nodes())),
                         p=P, size=2).tolist()

    _, D = spread_reach(G, S, Select, activation_probability, T)
    print (D)

    for u in G.nodes():
        if u in S:
            G.nodes[u]['weight'] = 1.0
        else:
            G.nodes[u]['weight'] = D[u]

    nx.write_gml(G, 'Save' + str(i) + '.gml')
