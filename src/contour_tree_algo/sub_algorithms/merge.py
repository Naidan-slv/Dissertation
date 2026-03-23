"""
Merge -- Combine join and split trees into the contour tree.

Based on:
    Carr, H., Snoeyink, J., Axen, U. (2003).
    Algorithm 7.3 (Merge), p. 47.
"""


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

    return deduped