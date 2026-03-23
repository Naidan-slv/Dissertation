"""
Merge -- Combine join and split trees into the contour tree.

Based on:
    Carr, H., Snoeyink, J., Axen, U. (2003).
    Algorithm 7.3 (Merge), p. 47.
"""

from collections import defaultdict


def _has_path(start, end, adj):
    """DFS check for existing path between two vertices."""
    if start == end:
        return True
    visited = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        for neighbor in adj.get(node, []):
            if neighbor == end:
                return True
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
    return False


def _remove_redundant_edges(edges):
    """Build a spanning tree by rejecting edges that would create cycles."""
    result = []
    adj = defaultdict(list)
    for u, v in edges:
        if _has_path(v, u, adj):
            continue
        result.append((u, v))
        adj[u].append(v)
        adj[v].append(u)
    return result


def merge_trees(join_edges: list, split_edges: list) -> list:
    """
    Merge join tree J(T) and split tree S(T) into contour tree T.

    Algorithm 7.3: combine edges from both trees, removing
    redundant edges that would create cycles.
    """
    all_edges = list(join_edges) + list(split_edges)
    edge_set = set(all_edges)

    # Deduplicate opposite-direction edges: (u,v) and (v,u) represent the same arc
    deduped = []
    seen_pairs = set()
    for u, v in edge_set:
        pair = tuple(sorted([u, v]))
        if pair not in seen_pairs:
            deduped.append((u, v))
            seen_pairs.add(pair)

    return _remove_redundant_edges(deduped)