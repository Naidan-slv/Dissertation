"""
Synthetic datasets for testing contour tree implementation.

Each dataset returns a Mesh instance.

These are intentionally small so the join/split behaviour
can be computed by hand and verified step-by-step.
"""

from mesh import TwoDimensionalMesh


def single_peak():
    """
    Dataset 1: Single Peak (No Joins)

    Structure:

        100 - 50 - 0
    """

    values = {
        0: 0,
        1: 50,
        2: 100
    }

    edges = [
        (2, 1),
        (1, 0)
    ]

    return TwoDimensionalMesh(values, edges)


def two_peaks_merge():
    """
    Dataset 2: Two Peaks Merging at One Join

    Structure:

       80  70
        \  /
        50
        |
        0

    """
    values = {
        0: 0,
        1: 50,
        2: 80,
        3: 70
    }

    edges = [
        (2, 1),  # 80 connected to 50
        (3, 1),  # 70 connected to 50
        (1, 0)   # 50 connected to 0
    ]

    return TwoDimensionalMesh(values, edges)


def three_peaks_merge():
    """
    Dataset 3: Three Peaks Merging at One Join

    Structure:

        100 90  80
           \  | /
             50
            |
            0
    """

    values = {
        0: 0,
        1: 50,
        2: 100,
        3: 90,
        4: 80
    }

    edges = [
        (2, 1),  # 100 → 50
        (3, 1),  # 90  → 50
        (4, 1),  # 80  → 50
        (1, 0)   # 50  → 0
    ]

    return TwoDimensionalMesh(values, edges)
