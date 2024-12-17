import sage.all as sg

def get_metric_dimension(G):

    V = G.vertices()
    # we prepare a ILP that minimizes the number of vertices we take
    lp = sg.MixedIntegerLinearProgram(maximization=False)
    x = lp.new_variable(binary=True)
    lp.set_objective(sum(x[v] for v in V))

    # compare every two vertices' distance to every other vertix
    for u in V:
        for v in V[u+1 : len(V)]:
            # if the distance is different, that vertix is possible
            vertices = [w for w in V if G.distance(w, u) != G.distance(w, v)]
            lp.add_constraint(sum(x[w] for w in vertices) >= 1)

    lp.solve()

    resolving_set = [v for v in V if lp.get_values(x[v]) == 1]
    return resolving_set, len(resolving_set)


def get_edge_to_vertex_distances(G):
    M = G.adjacency_matrix()
    distances = G.distance_all_pairs()

    # dictionary that will hold distances from edges to all vertices
    dist_to_edges = {}

    # iterate through every edge
    for i in range(M.nrows()):
        for j in range(i+1, M.nrows()):
            if M[i][j] != 1:
                continue
            list_of_dist_to_uv = list(zip(list(distances[i].values()), list(distances[j].values())))
            # distance to edge is distance to the nearer vertix on that edge
            dist_to_edges[(i,j)] = [min(tup) for tup in list_of_dist_to_uv]

    return dist_to_edges


def get_edge_metric_dimension(G, dist_to_edges):
    M = G.adjacency_matrix()
    E = G.edges(labels=False)
    V = G.vertices()
    # distances = G.distance_all_pairs()

    lp = sg.MixedIntegerLinearProgram(maximization=False)
    x = lp.new_variable(binary=True)
    lp.set_objective(sum(x[v] for v in V))

    # comparing every pair of edges
    for e_ix in range(len(E)):
        for f_ix in range(e_ix + 1, len(E)):
            dist_to_e = dist_to_edges[E[e_ix]]
            dist_to_f = dist_to_edges[E[f_ix]]
            vertices = [v for v in V if dist_to_e[v] != dist_to_f[v]]

            lp.add_constraint(sum(x[w] for w in vertices) >= 1)

    lp.solve()

    resolving_set = [v for v in V if lp.get_values(x[v]) == 1]
    return resolving_set, len(resolving_set)


def get_mixed_metric_dimension(G, dist_to_edges):
    M = G.adjacency_matrix()
    E = G.edges(labels=False)
    V = G.vertices()
    v_distances = G.distance_all_pairs()

    lp = sg.MixedIntegerLinearProgram(maximization=False)
    x = lp.new_variable(binary=True)
    lp.set_objective(sum(x[v] for v in V))

    v_distances.update(dist_to_edges)
    all_distances = list(v_distances.items())

    # comparing every pair of edges, vertices and mixed pairs
    for i in range(len(all_distances)):
        for j in range(i + 1, len(all_distances)):
            dist_to_i = all_distances[i][1]
            dist_to_j = all_distances[j][1]
            vertices = [v for v in V if dist_to_i[v] != dist_to_j[v]]

            lp.add_constraint(sum(x[w] for w in vertices) >= 1)

    lp.solve()

    resolving_set = [v for v in V if lp.get_values(x[v]) == 1]
    return resolving_set, len(resolving_set)

correct_graphs_eq = []
correct_graphs_mdim = []

for n in range(1,9):
    for g in sg.graphs.nauty_geng("{0} -c".format(n)):

        _, dim = get_metric_dimension(g)
        dist_to_edges = get_edge_to_vertex_distances(g)
        _, edim = get_edge_metric_dimension(g, dist_to_edges)
        _, mdim = get_mixed_metric_dimension(g, dist_to_edges)

        if dim == edim == mdim:
            correct_graphs_eq.append(g)
            print(dim)
            print(g.vertices())
        elif mdim == dim + edim:
            correct_graphs_mdim.append(g)
            print(dim, edim, mdim)
            print(g.vertices())
