"""Viewer payload helpers for Carr-style simplification context.

References: Carr (2004) Ch. 11 for collapse records and Weber et al. (2007)
for the display motivation. This remains tree/context display only.
"""


def build_simplification_payload(
    supernodes,
    superarcs,
    value_fn,
    isovalue=None,
    mode="height",
    threshold=None,
    target_edges=None,
):
    raise NotImplementedError
