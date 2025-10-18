import networkx as nx
import matplotlib.pyplot as plt

from numpy.linalg import matrix_power
from Social.constants import *
from Func import *


def sort_expendables(G, G_E):

    E_rem = [(u, v) for (u, v) in G.edges() if (u, v) not in G_E.edges()]
    E_rem = sorted(E_rem, key=lambda edge: G.in_degree(edge[0]))
    print (E_rem)

    return E_rem


def rewire(G, activate):
    while True:
        (u1, v1), (u2, v2) = random.sample(list(G.edges()), 2)
        if u1 != u2 or v1 != v2 and (u1 != u2 and v1 != v2):
            G.remove_edge(u1, v1)
            G.remove_edge(u2, v2)
            G.add_edge(u1, v2)
            G.add_edge(u2, v1)
            break
    return G, (u1, v1), (u2, v2)


def reach2(g, S, T, activation_probability, mc=10000):
    Z_All = {u: 0 for u in g.nodes()}
    for u in g.nodes():
        g.nodes[u]['active'] = 1 if u in S else 0

    for _ in range(mc):
        Active_all, t = list(S), 1
        Done = np.zeros((len(g), len(g)))

        for u in S:
            g.nodes[u]['active'] += 1 / mc
            Z_All[u] += 1 / mc

        A = list(S)
        while t < T:
            A_new = []
            for u in A:
                for v in g.successors(u):
                    if t <= g[u][v]['weight'] and not Done[u, v] and v not in Active_all:
                        if random.random() < activation_probability:
                            A_new.append(v)
                            g.nodes[v]['active'] += 1 / mc
                            Z_All[v] += 1 / mc
                        Done[u, v] = 1
            Active_all.extend(A)
            A = A_new
            t += 1

    return g, Z_All


def mode_run(G0, S, T, activate, Select, S0, max_iterate):
    iterate = 0
    while iterate < max_iterate:
        E = [(u, v) for u in G0.nodes() for v in G0.nodes() if u != v and (u, v) not in G0.edges()]
        u, v = random.choice(E)
        G0.add_edge(u, v)
        S1 = spread_reach(G0, S, Select, aP, T)
        iterate += 1
    return S1, iterate


def gen(G, si):
    H = G.to_undirected()
    dsum = float(sum(H.degree(u) for u in H.nodes()))
    g = nx.DiGraph()

    r = np.random.choice(G.nodes(), 1, p=[H.degree(u) / dsum for u in G.nodes()])
    g.add_node(int(r[0]))

    while len(g) < si:
        nset = [v for u in g.nodes() for v in H.neighbors(u) if v not in g.nodes()]
        if not nset:
            return g
        r = random.choice(nset)
        new_edges = [(u, r) for u in g.nodes() if G.has_edge(u, r)]
        new_edges += [(r, u) for u in g.nodes() if G.has_edge(r, u)]
        g.add_edges_from(new_edges)
    return g


def ego(G, S, K):
    G_E = nx.DiGraph()
    for s in S:
        for u, v in nx.ego_graph(G, s, radius=K).edges():
            G_E.add_edge(u, v)
    return G_E


def score_each_link(First, G, G_E, Ac0, AcList0, S, K, aP, mode, new_ones, Scores, Select):
    if mode == 0:
        Scores = {(u, v): 0 for (u, v) in G.edges()}
        Check = list(First.keys())
    else:
        Check = deepcopy(new_ones)

    for (u, v) in Check:
        # If first score is 0, the total score is 0
        if First[(u, v)] == 0:
            Scores[(u, v)] = 0
            continue

        # If v does not connect ego network nodes, total score is 0
        reachable_v = [w for w in G_E.nodes() if nx.has_path(G_E, v, w) and v != w and w in Select]
        if not reachable_v:
            Scores[(u, v)] = 0
            continue

        Ac1 = deepcopy(Ac0)
        Ac1[u, v] = aP
        AcList1 = [matrix_power(Ac1, k + 1) for k in range(K)]
        Second0 = sum(AcList0[k][s, w] for k in range(K) for s in S for w in reachable_v)
        Second1 = sum(AcList1[k][s, w] for k in range(K) for s in S for w in reachable_v)

        # The difference between second1 and second0 is the improvement by adding the new link (u, v)
        Scores[(u, v)] = First[(u, v)] * max(0, Second1 - Second0)

    return {k: v for k, v in Scores.items() if k[0] != k[1]}


def main_score(G, G_E, Ac0, S, aP, K, Select, mode, umax, vmax, Scores, added_edges):
    # Make the weights for all non-ego nodes equal to 0.
    for i in range(A.shape[0]):
        if i not in G_E.nodes():
            Ac0[i, :] = 0
            Ac0[:, i] = 0

    AcList0 = [matrix_power(Ac0, k + 1) for k in range(K)]
    # All possible edges (u, v) should have
    # (1) u != v; (2) v not in S; and (3) (u, v) not in the existing edges
    First = {(u, v): sum(AcList0[k][s, u] for k in range(K) for s in S)
             for u in G_E.nodes() for v in G_E.nodes()
             if (u, v) not in G.edges() and u != v and v not in S}

    # Make the first scores for already added edges equal to 0
    for (u, v) in First.keys():
        if (u, v) in added_edges:
            First[(u, v)] = 0

    if mode == 0:
        return score_each_link(First, G, G_E, Ac0, AcList0, S, K, aP, 0, None, None, Select)

    # New edges being considered should be in the ego network
    # and not be part of already added edges
    new_ones = [(u, v) for (u, v) in Scores if u in G_E.nodes() and v in G_E.nodes()
                and (nx.has_path(G_E, vmax, u) or nx.has_path(G_E, v, umax)) and (u, v) not in added_edges]
    for (u, v) in new_ones:
        First[(u, v)] = sum(AcList0[k][s, u] for k in range(K) for s in S)

    return score_each_link(First, G, G_E, Ac0, AcList0, S, K, aP, 0, new_ones, Scores, Select)


def sparsify(G, p=0.5):
    E = list(G.edges())
    rem = np.random.choice(len(E), size=int(p * len(E)), replace=False)
    G.remove_edges_from([E[i] for i in rem])
    return G


def gen_weighted_random(n, pE, aP, fname):
    H = nx.read_gml(fname)
    H = nx.convert_node_labels_to_integers(H)
    G = gen(H, n)
    G = nx.convert_node_labels_to_integers(G)
    for u, v in G.edges():
        G[u][v]['weight'] = aP
    return G


# ==== MAIN EXECUTION ====
I = 100
data_dir = '/Users/sr0215/Python/Social/'
pE = .03

for iterate in range(I):

    print(f'\nIteration {iterate}')
    while True:
        G = gen_weighted_random(n, pE, aP, data_dir + 'Ecoli.gml')
        if len(G) >= n:
            break

    # Sparsify network and convert to adjacency matrix (A)
    G = sparsify(G)
    A = nx.adjacency_matrix(G).todense()

    # Select seed nodes (S)
    N = sorted(G.nodes())
    P = [G.out_degree(u) for u in N]
    P = [val / sum(P) for val in P]
    S = np.random.choice(N, p=P, size=nS, replace=False).tolist()
    print(S)

    # Form ego network of G (G_E)
    G_E = ego(G, S, K)

    # Sort edges (u, v) not in G_E by the in_degree of u.
    E_rem = sort_expendables(G, G_E)

    # Select (a subset of all) nodes as targets
    Select = deepcopy(N)

    G0 = deepcopy(G)

    # Calculate spread in G when nodes in S are active
    max_spread0 = spread_reach(G0, S, Select, aP, T)
    print(f'Spread in original {max_spread0}')

    y = [0]
    isFirst, h = True, 0
    Scores, umax, vmax = None, None, None
    added_edges = []

    while h < how_many_switches:
        Scores = main_score(G, G_E, deepcopy(A), S, aP, K, Select, 0 if isFirst else 1, umax, vmax, Scores, added_edges)
        isFirst = False

        umax, vmax = max(Scores, key=Scores.get)
        added_edges.append((umax, vmax))
        del Scores[(umax, vmax)]

        G.add_edge(umax, vmax)
        (u_rem, v_rem) = E_rem.pop(0)
        G.remove_edge(u_rem, v_rem)

        G_E.add_edge(umax, vmax)

        max_spread = spread_reach(G, S, Select, aP, T)
        print(f'Edge ({umax, vmax}) with spread {max_spread - max_spread0}')
        print (f'Number of edges in G are {len(G.edges())}')

        y.append(max_spread - max_spread0)
        h += 1

    rS, iS = mode_run(G0, S, T, aP, Select, max_spread0, how_many_switches)
    print(f'Random switch has spread of {rS - max_spread0} after {iS} iterations.')

    Y.append(y)
    Y3.append([y[-1], rS - max_spread0, iS])
    Z = np.array(Y)

    print([np.mean(Z[:, i]) * len(G) for i in range(Z.shape[1])])
    print([np.mean([Y3[j][i] * len(G) for j in range(len(Y3))]) for i in range(3)])

    mn1.append(np.mean([Y3[j][0] for j in range(len(Y3))]))
    mn2.append(np.mean([Y3[j][1] for j in range(len(Y3))]))
    sd1.append(np.std([Y3[j][0] for j in range(len(Y3))]))
    sd2.append(np.std([Y3[j][1] for j in range(len(Y3))]))

    plt.plot(range(len(mn1)), mn1, label='Scoring', color='red')
    plt.plot(range(len(mn2)), mn2, label='Sampling', color='green')
    plt.fill_between(range(len(mn1)), np.array(mn1) - np.array(sd1),
                     np.array(mn1) + np.array(sd1), color='red', alpha=0.1)
    plt.fill_between(range(len(mn2)), np.array(mn2) - np.array(sd2),
                     np.array(mn2) + np.array(sd2), color='green', alpha=0.1)
    plt.legend()
    plt.savefig('Increment.png', dpi=300)
    plt.close()