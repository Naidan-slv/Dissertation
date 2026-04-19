"""
Export a contour tree (supernodes + superarcs) to Graphviz DOT format.

Node classification follows Carr, Snoeyink & Axen (2003) Section 3.1:
leaves of the contour tree are local extrema (min or max), and branch
points (degree >= 3) are saddles.

DOT/Graphviz output for contour tree debugging is recommended in
Carr, Tierny & Weber (2020) Section 7.

Colour convention (blue=min, red=max) follows Tierny et al. (2018) TTK.
"""


from collections import defaultdict


def classify_nodes(supernodes, superarcs, value_fn):
    """Classify each supernode as min, max, or saddle based on
    its degree in the tree and its scalar value relative to neighbours."""
    deg = defaultdict(int)
    for u, v in superarcs:
        deg[u] += 1
        deg[v] += 1

    result = {}
    for n in supernodes:
        if deg[n] == 1:
            # leaf — compare to its single neighbour to decide min vs max
            nbr = next(v if u == n else u for u, v in superarcs if u == n or v == n)
            result[n] = "min" if value_fn(n) < value_fn(nbr) else "max"
        else:
            result[n] = "saddle"
    return result


COLOURS = {"min": "lightblue", "max": "tomato", "saddle": "lightgrey"}
SHAPES  = {"min": "ellipse",   "max": "ellipse",  "saddle": "diamond"}


def ct_to_dot(supernodes, superarcs, value_fn):
    """Build a DOT-language string for the given contour tree."""
    labels = classify_nodes(supernodes, superarcs, value_fn)

    lines = ["graph contour_tree {", "    rankdir=BT;"]
    for n in supernodes:
        kind = labels[n]
        lbl = f"{n}\\nval={value_fn(n)}\\n({kind})"
        lines.append(
            f'    {n} [label="{lbl}" '
            f'style=filled fillcolor={COLOURS[kind]} '
            f'shape={SHAPES[kind]}];'
        )
    for u, v in superarcs:
        lines.append(f"    {u} -- {v};")
    lines.append("}")
    return "\n".join(lines)


def save_dot(dot_str, path):
    """Write a DOT string out to a file."""
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(dot_str)
