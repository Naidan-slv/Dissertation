"""
Merge -- Combine join and split trees into the contour tree.

Algorithm 7.3 from Carr, Snoeyink, Axen (2003), p. 47.

Uses directed leaf-removal with splice:

    CT-degree(v) = upDegJ(v) + downDegS(v)

where
    upDegJ(v)  = # of J-neighbours with higher scalar value  (J-children)
    downDegS(v) = # of S-neighbours with lower scalar value  (S-children)

A contour tree leaf has CT-degree == 1:
    - Upper leaf (upDegJ == 0): transfer J-edge to CT, splice v out of S
    - Lower leaf (downDegS == 0): transfer S-edge to CT, splice v out of J

Splice reconnects v's children in the other tree to v's parent,
keeping adjacency lists consistent so future parent-lookups succeed.

This is O(n) — each vertex is processed exactly once.
"""

from collections import defaultdict, deque


def merge_trees(join_edges: list, split_edges: list, value_fn) -> list:
    """
    Merge join tree and split tree into the contour tree.

    Algorithm 7.3: directed leaf-removal with splice.

    Args:
        join_edges:  List of (u, v) edges from the join tree.
        split_edges: List of (u, v) edges from the split tree.
        value_fn:    Callable mapping vertex id → scalar value.

    Returns:
        List of (u, v) edges forming the contour tree (n-1 edges for n vertices).
    """
    # Build mutable undirected adjacency for both trees
    j_adj = defaultdict(set)
    s_adj = defaultdict(set)

    for u, v in join_edges:
        j_adj[u].add(v)
        j_adj[v].add(u)
    for u, v in split_edges:
        s_adj[u].add(v)
        s_adj[v].add(u)

    all_verts = set(j_adj.keys()) | set(s_adj.keys())
    n = len(all_verts)

    if n <= 1:
        return []

    # Cache scalar values for speed
    val = {v: value_fn(v) for v in all_verts}

    # Tie-breaking consistent with the sweep algorithms:
    # u is "higher" than v if f(u) > f(v), or f(u) == f(v) and u > v
    def higher(u, v):
        return val[u] > val[v] or (val[u] == val[v] and u > v)

    # Compute directed degrees:
    #   upDegJ[v]  = # of J-neighbours strictly "higher" than v  (J-children)
    #   downDegS[v] = # of S-neighbours strictly "lower" than v  (S-children)
    upDegJ = {}
    downDegS = {}
    for v in all_verts:
        upDegJ[v] = sum(1 for u in j_adj[v] if higher(u, v))
        downDegS[v] = sum(1 for u in s_adj[v] if higher(v, u))

    # Seed the queue with initial CT-leaves (CT-degree == 1)
    queue = deque()
    for v in all_verts:
        if upDegJ[v] + downDegS[v] == 1:
            queue.append(v)

    ct_edges = []

    while len(ct_edges) < n - 1 and queue:
        v = queue.popleft()
        if v not in upDegJ:          # already removed
            continue
        if upDegJ[v] + downDegS[v] != 1:
            continue                  # stale queue entry

        candidates = []               # vertices to check as potential new leaves

        if upDegJ[v] == 0:
            # ── Upper leaf: transfer J-edge ──
            # v's sole J-neighbour is its J-parent (lower value, degree 1 in J)
            u = next(iter(j_adj[v]))
            ct_edges.append((v, u))

            # Remove v from J: u loses v as an upward child
            j_adj[u].discard(v)
            upDegJ[u] -= 1
            candidates.append(u)

            # Splice v out of S: reconnect v's S-children to v's S-parent
            s_par = None
            s_children = []
            for w in s_adj[v]:
                s_adj[w].discard(v)
                if higher(w, v):
                    s_par = w
                else:
                    s_children.append(w)
            if s_par is not None:
                for c in s_children:
                    s_adj[s_par].add(c)
                    s_adj[c].add(s_par)
                # s_par lost child v, gained v's children
                downDegS[s_par] = downDegS[s_par] - 1 + len(s_children)
                candidates.append(s_par)

        else:
            # ── Lower leaf (downDegS == 0): transfer S-edge ──
            # v's sole S-neighbour is its S-parent (higher value, degree 1 in S)
            u = next(iter(s_adj[v]))
            ct_edges.append((v, u))

            # Remove v from S: u loses v as a downward child
            s_adj[u].discard(v)
            downDegS[u] -= 1
            candidates.append(u)

            # Splice v out of J: reconnect v's J-children to v's J-parent
            j_par = None
            j_children = []
            for w in j_adj[v]:
                j_adj[w].discard(v)
                if higher(v, w):       # w has lower value → J-parent
                    j_par = w
                else:
                    j_children.append(w)
            if j_par is not None:
                for c in j_children:
                    j_adj[j_par].add(c)
                    j_adj[c].add(j_par)
                # j_par lost child v, gained v's children
                upDegJ[j_par] = upDegJ[j_par] - 1 + len(j_children)
                candidates.append(j_par)

        # Clean up v
        del upDegJ[v]
        del downDegS[v]
        j_adj[v].clear()
        s_adj[v].clear()

        # Check if any affected vertex became a new CT-leaf
        for c in candidates:
            if c in upDegJ and upDegJ[c] + downDegS[c] == 1:
                queue.append(c)

    return ct_edges