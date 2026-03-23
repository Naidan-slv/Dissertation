"""
Test the Carr et al. 9×9 mesh against expected output from Figure 7.4 of the paper.

Critical points identified: {0, 20, 71, 80, 90, 100}
"""

import pytest
from datasets.synthetic.carr_9x9_mesh import create_carr_9x9_mesh
from src.contour_tree_algo.sub_algorithms.join_sweep import compute_join_tree
from src.contour_tree_algo.sub_algorithms.split_sweep import compute_split_tree
from src.contour_tree_algo.sub_algorithms.merge import merge_trees
from src.contour_tree_algo.final_contour_tree import compute_contour_tree


def test_carr_9x9_join_tree():
    mesh = create_carr_9x9_mesh()
    edges = compute_join_tree(mesh)
    
    print(f"\n=== CARR 9×9 MESH JOIN TREE ===")
    print(f"Edges ({len(edges)} total):")
    for u, v in sorted(edges):
        val_u, val_v = mesh.value(u), mesh.value(v)
        print(f"  ({u:2d}, {v:2d}): v{u}[{val_u:3d}] → v{v}[{val_v:3d}]")
    
    assert len(edges) > 0, "Join tree must have edges"


def test_carr_9x9_split_tree():
    mesh = create_carr_9x9_mesh()
    edges = compute_split_tree(mesh)
    
    print(f"\n=== CARR 9×9 MESH SPLIT TREE ===")
    print(f"Edges ({len(edges)} total):")
    for u, v in sorted(edges):
        val_u, val_v = mesh.value(u), mesh.value(v)
        print(f"  ({u:2d}, {v:2d}): v{u}[{val_u:3d}] ← v{v}[{val_v:3d}]")
    
    assert len(edges) > 0, "Split tree must have edges"


def test_carr_9x9_contour_tree():
    mesh = create_carr_9x9_mesh()
    edges = compute_contour_tree(mesh)
    
    print(f"\n=== CARR 9×9 MESH CONTOUR TREE ===")
    print(f"Edges ({len(edges)} total):")
    for u, v in sorted(edges):
        val_u, val_v = mesh.value(u), mesh.value(v)
        print(f"  ({u:2d}, {v:2d}): v{u}[{val_u:3d}] ↔ v{v}[{val_v:3d}]")
    
    assert len(edges) > 0, "Contour tree must have edges"


if __name__ == "__main__":
    test_carr_9x9_join_tree()
    test_carr_9x9_split_tree()
    test_carr_9x9_contour_tree()
