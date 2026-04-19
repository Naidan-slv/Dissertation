"""
Export a contour tree (supernodes + superarcs) to Graphviz DOT format.

Node classification follows Carr, Snoeyink & Axen (2003) Section 3.1:
leaves of the contour tree are local extrema (min or max), and branch
points (degree >= 3) are saddles.

DOT/Graphviz output for contour tree debugging is recommended in
Carr, Tierny & Weber (2020) Section 7.

Colour convention (blue=min, red=max) follows Tierny et al. (2018) TTK.
"""


def classify_nodes(supernodes, superarcs, value_fn):
    """Classify each supernode as min, max, or saddle based on
    its degree in the tree and its scalar value relative to neighbours."""
    raise NotImplementedError


def ct_to_dot(supernodes, superarcs, value_fn):
    """Build a DOT-language string for the given contour tree."""
    raise NotImplementedError


def save_dot(dot_str, path):
    """Write a DOT string out to a file."""
    raise NotImplementedError
