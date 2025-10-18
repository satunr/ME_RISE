# https://websites.umich.edu/~mejn/netdata/
# https://networkrepository.com/index.php
import networkx as nx
import random
import time
from numpy.linalg import matrix_power
from Social.constants import *
from copy import deepcopy
from Func import *
from Rearrange import *


def ego(G, S, K):
    G_E = nx.DiGraph()
    for s in S:
        E = nx.ego_graph(G, s, radius=K)
        for (u, v) in E.edges():
            if (u, v) not in G_E.edges():
                G_E.add_edge(u, v)

    return G_E


def reach(AL, s, u):
    reachability = 0.0
    for k in range(AL):
        reachability += AL[k][s, u]

    return reachability


def score_each_link(First, G, G_E, Ac0, AcList0, S, K, aP, Select):
    # Calculate the second scores for each link (u, v): change in reach from s to v'
    # by adding (u, v), where v' is the node reachable from v in G_E
    Scores = {(u, v): 0 for (u, v) in G.edges()}
    for (u, v) in First.keys():
        if First[(u, v)] == 0:
            Scores[(u, v)] = 0
            continue

        reachable_v = [w for w in G_E.nodes() if nx.has_path(G_E, v, w) and v != w and w in Select]
        if len(reachable_v) == 0:
            continue

        Ac1 = deepcopy(Ac0)
        Ac1[u, v] = aP
        AcList1 = [matrix_power(Ac1, k + 1) for k in range(K)]

        Second0 = sum([AcList0[k][s, w] for k in range(K) for s in S for w in reachable_v])
        Second1 = sum([AcList1[k][s, w] for k in range(K) for s in S for w in reachable_v])

        if Second0 != Second1:
            Scores[(u, v)] = First[(u, v)] * (Second1 - Second0)

    Scores = {(u, v): Scores[(u, v)] / max(list(Scores.values()))
    if max(list(Scores.values())) > 0 else 0 for (u, v) in Scores.keys()}

    return Scores


def main_score(G, G_E, A, S, aP, K, Select):
    # G, G_E, deepcopy(A), S, aP, K, Select
    # # Remove all non-zero entries in rows and columns not in G_E
    # for i in range(A.shape[0]):
    #     if i not in G_E.nodes():
    #         Ac0[i, :] = 0
    #         Ac0[:, i] = 0

    # # NO Optimization Step
    # Ac0 = deepcopy(A)

    # Optimization Step
    G = deepcopy(G_E)
    Ac0 = deepcopy(A[:len(G_E), :len(G_E)])

    print ('Note change.', A.shape, Ac0.shape)

    # Generate powers of adjacency matrix
    AcList0 = [matrix_power(Ac0, k + 1) for k in range(K)]

    # Calculate the first scores for each link (u, v):
    # connectivity from seeds to node u
    First = {(u, v): sum([AcList0[k][s, u]
                          for k in range(K) for s in S])
    if ((u, v) not in G.edges() and u != v) else 0 for u in G_E.nodes() for v in G_E.nodes()}
    First = {e: First[e] for e in First.keys()}

    Scores = score_each_link(First, G, G_E, Ac0, AcList0, S, K, aP, Select)

    return Scores


def gen_weighted_random(n, pE, aP, fname):
    # Create a directed graph
    # G = nx.erdos_renyi_graph(n, p = pE, directed = True)

    H = nx.read_gml(fname)
    H = nx.convert_node_labels_to_integers(H, first_label=0)

    G = gen(H, n)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    print(G)

    for (u, v) in G.edges():
        G[u][v]['weight'] = aP
        # G[u][v]['weight'] = random.uniform(0, 1)

    return G


def gen(G, si):
    H = G.to_undirected()
    dsum = float(sum([H.degree(u) for u in H.nodes()]))

    # New subgraph
    g = nx.DiGraph()

    # Pick random seed as a starting node
    r = np.random.choice(G.nodes(), 1, p=[float(H.degree(u)) / float(dsum) for u in G.nodes()])
    g.add_node(int(r[0]))

    while len(g) < si:
        nset = []

        # List of all neighbors of nodes in g
        for u in g.nodes():
            l = H.neighbors(u)
            nset.extend(l)

        # The nodes in 'nset' are not already present in g
        nset = [u for u in nset if u not in g.nodes()]

        if len(nset) == 0:
            return g

        r = random.choice(nset)
        new_edges = []
        for u in g.nodes():
            if G.has_edge(u, r):
                new_edges.append((u, r))

            if G.has_edge(r, u):
                new_edges.append((r, u))

        g.add_edges_from(new_edges)

    return g


for iterate in range(I):
    print(f'\nIteration {iterate}')

    while True:
        # Generate weighted graph and adjacency matrix
        G = gen_weighted_random(n, pE, aP, 'Email_Now.gml')
        # G = nx.read_gml('Email_Now.gml')
        # G = nx.convert_node_labels_to_integers(G, first_label=0)

        if len(G) >= n:
            break

    A = nx.adjacency_matrix(G).todense()
    print('Original graph information:', G)

    # Find seed nodes
    N = list(sorted(G.nodes()))
    P = [G.out_degree(u) for u in N]
    P = [val / sum(P) for val in P]
    S = np.random.choice(a=N, p=P, size=nS, replace=False).tolist()
    # print (S)

    # Create ego network for the given seed set
    G_E = ego(G, S, K)

    G, G_E, A, S = arrange(G, G_E, S)
    print ('Ego. ', list(sorted(G_E.nodes())))

    Select = deepcopy(N)
    # Select = np.random.choice(a = N, size = select, replace = False).tolist()

    t0 = time.time()

    # Find the score for each link
    Scores = main_score(G, G_E, deepcopy(A), S, aP, K, Select)
    print(sorted(Scores.items(), key=lambda x: x[1], reverse=True))

    '''
    # Render as graph-ml file
    mScore = min(list(Scores.values()))
    H = nx.DiGraph()
    H.add_nodes_from(list(G.nodes()))

    for (u, v) in Scores.keys():
        H.add_edge(u, v)
        H[u][v]['score'] = Scores[(u, v)]

    for u in H.nodes():
        if u in S:
            H.nodes[u]['Status'] = 0
        elif u in G_E.nodes():
            H.nodes[u]['Status'] = 1
        else:
            H.nodes[u]['Status'] = 2

    nx.write_gml(H, 'Scores.gml')
    '''

    # Spread estimation
    (umax, vmax) = max(Scores, key=Scores.get)
    del Scores[(umax, vmax)]

    # Calculate the mean spread of missing edges with NOT the best score (B')
    spread_all = []
    for u in G.nodes():
        for v in G.nodes():
            if u == v and (u, v) not in G.edges() and (u != umax and v != vmax):
                H = deepcopy(G)
                H.add_edge(u, v)
                spread, _ = spread_reach(H, S, Select, aP, T)
                spread_all.append(spread)

    # Calculate the spread of missing edges with the best score (B)
    H = deepcopy(G)
    H.add_edge(umax, vmax)

    RT.append(time.time() - t0)

    H = remove_edge_outside_ego(H, G, G_E)
    print('Modified graph information:', G)

    max_spread, _ = spread_reach(H, S, Select, aP, T)
    print(f'Maximum spread is after adding chosen link is {max_spread}')

    Acc = [Acc[0], Acc[1] + 1]
    if max_spread >= np.mean(spread_all):
        Acc = [Acc[0] + 1, Acc[1]]
        al.append(1)
    else:
        al.append(0)
    print(Acc, np.mean(RT),np.std(RT))

    # if len(al) > 10:
    #     S = stats.ttest_1samp(al, popmean=0.5, alternative='greater')
    #     print(f'P-value: {S.pvalue}')
    #     Y.append(S.pvalue)
    # else:
    #     Y.append(1.0)

    # L1.append(max_spread)
    # L2.append(np.mean(spread_all))

    # p_value = permutation_test(L1, L2)
    # print (f'P-value: {p_value}')

    # plt.plot([i for i in range(len(Y))], Y)
    # plt.xlabel('Iterations')
    # plt.ylabel('P-value')
    # plt.savefig('P-value.png')

