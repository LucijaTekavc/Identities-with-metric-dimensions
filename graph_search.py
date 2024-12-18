import sage.all as sg
import itertools
import time
import sys
import os


def get_metric_dimension(G):
    V = G.vertices()
    assert V == list(range(len(V)))
    # we prepare a ILP that minimizes the number of vertices we take
    lp = sg.MixedIntegerLinearProgram(maximization=False)
    x = lp.new_variable(binary=True)
    lp.set_objective(sum(x[v] for v in V))

    # compare every two vertices' distance to every other vertex
    for u, v in itertools.combinations(V, 2):
        # if the distance is different, that vertex is possible
        vertices = [w for w in V if G.distance(w, u) != G.distance(w, v)]
        lp.add_constraint(sum(x[w] for w in vertices) >= 1)

    lp.solve()

    resolving_set = [v for v in V if lp.get_values(x[v]) == 1]
    metric_dimension = len(resolving_set)
    return metric_dimension


def get_edge_to_vertex_distances(G):
    M = G.adjacency_matrix()
    distances = G.distance_all_pairs()

    # dictionary that will hold distances from edges to all vertices
    dist_to_edges = {}

    # iterate through every edge
    for i, j in itertools.combinations(range(M.nrows()), 2):
        if M[i][j] != 1:
            continue
        list_of_dist_to_uv = zip(distances[i].values(), distances[j].values())
        # distance to edge is distance to the nearer vertex on that edge
        dist_to_edges[(i,j)] = {
            index: min(tup) for index, tup in enumerate(list_of_dist_to_uv)
        }

    return dist_to_edges


def get_edge_metric_dimension(G, dist_to_edges):
    M = G.adjacency_matrix()
    E = G.edges(labels=False)
    V = G.vertices()

    lp = sg.MixedIntegerLinearProgram(maximization=False)
    x = lp.new_variable(binary=True)
    lp.set_objective(sum(x[v] for v in V))

    # comparing every pair of edges
    for e_ix, f_ix in itertools.combinations(range(len(E)), 2):
        dist_to_e = dist_to_edges[E[e_ix]]
        dist_to_f = dist_to_edges[E[f_ix]]
        vertices = [v for v in V if dist_to_e[v] != dist_to_f[v]]

        lp.add_constraint(sum(x[w] for w in vertices) >= 1)

    lp.solve()

    resolving_set = [v for v in V if lp.get_values(x[v]) == 1]
    edge_metric_dimension = len(resolving_set)
    return edge_metric_dimension


def get_mixed_metric_dimension(G, dist_to_edges):
    M = G.adjacency_matrix()
    E = G.edges(labels=False)
    V = G.vertices()
    v_distances = G.distance_all_pairs()
    v_distances.update(dist_to_edges)

    lp = sg.MixedIntegerLinearProgram(maximization=False)
    x = lp.new_variable(binary=True)
    lp.set_objective(sum(x[v] for v in V))

    # comparing every pair of edges, vertices and mixed pairs
    for (_, dist_to_i), (_, dist_to_j) in itertools.combinations(v_distances.items(), 2):
        vertices = [v for v in V if dist_to_i[v] != dist_to_j[v]]
        lp.add_constraint(sum(x[w] for w in vertices) >= 1)

    lp.solve()

    resolving_set = [v for v in V if lp.get_values(x[v]) == 1]
    mixed_metric_dimension = len(resolving_set)
    return mixed_metric_dimension


if __name__ == "__main__":
    if "eq_graphs" not in os.listdir():
        os.mkdir("eq_graphs")
    if "mdim_graphs" not in os.listdir():
        os.mkdir("mdim_graphs")
    correct_graphs_eq = []
    correct_graphs_mdim = []

    # read max_n from terminal argument if given
    # usage: python -i graph_search.py 99
    max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    for n in range(1, max_n + 1):
        print(f"n={n}")
        time_start = time.time()

        for i, g in enumerate(sg.graphs.nauty_geng("{0} -c".format(n)), start=1):
            if i % 100 == 0:
                print(f"  graph: {i:_}", end="\r")

            dim = get_metric_dimension(g)
            dist_to_edges = get_edge_to_vertex_distances(g)
            edim = get_edge_metric_dimension(g, dist_to_edges)
            mdim = get_mixed_metric_dimension(g, dist_to_edges)

            if dim == edim == mdim:
                g.export_to_file(f"eq_graphs/{n}_{i}_graph", format="gexf")
                correct_graphs_eq.append(g)
            elif mdim == dim + edim:
                g.export_to_file(f"mdim_graphs/{n}_{i}_graph", format="gexf")
                correct_graphs_mdim.append(g)


        time_elapsed = time.time() - time_start
        print(f"  total graphs: {i:_}")
        print(f"  time elapsed: {time_elapsed:.2f} s")
        print("")
