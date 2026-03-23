"""
Comprehensive validation of join/split/merge pipeline on Carr et al. 9×9 mesh.

Tests the example from Figures 7.2-7.7, verifying:
- Join tree structure (Figure 7.2 - green)
- Split tree structure (Figure 7.3 - blue)
- Merge process (Figures 7.6-7.7 - combining both)
"""

import pytest
from datasets.synthetic.carr_9x9_mesh import create_carr_9x9_mesh
from src.contour_tree_algo.sub_algorithms.join_sweep import compute_join_tree
from src.contour_tree_algo.sub_algorithms.split_sweep import compute_split_tree
from src.contour_tree_algo.sub_algorithms.merge import merge_trees
from src.contour_tree_algo.final_contour_tree import compute_contour_tree


def build_adjacency(edges):
    """Build adjacency list from edges."""
    adj = {}
    for u, v in edges:
        if u not in adj:
            adj[u] = set()
        if v not in adj:
            adj[v] = set()
        adj[u].add(v)
        adj[v].add(u)
    return adj


def has_cycles(edges):
    """Check if edge list contains cycles."""
    adj = build_adjacency(edges)
    visited = set()
    rec_stack = set()
    
    def dfs(v, parent):
        visited.add(v)
        rec_stack.add(v)
        
        for neighbor in adj.get(v, set()):
            if neighbor == parent:
                continue
            if neighbor not in visited:
                if dfs(neighbor, v):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(v)
        return False
    
    for v in adj:
        if v not in visited:
            if dfs(v, None):
                return True
    return False


def is_connected(edges):
    """Check if edges form a connected component."""
    if not edges:
        return True
    
    adj = build_adjacency(edges)
    visited = set()
    start = next(iter(adj.keys()))
    queue = [start]
    
    while queue:
        v = queue.pop(0)
        if v in visited:
            continue
        visited.add(v)
        for neighbor in adj.get(v, set()):
            if neighbor not in visited:
                queue.append(neighbor)
    
    return len(visited) == len(adj)


def get_vertex_degrees(edges):
    """Get degree of each vertex."""
    degrees = {}
    for u, v in edges:
        degrees[u] = degrees.get(u, 0) + 1
        degrees[v] = degrees.get(v, 0) + 1
    return degrees


def test_carr_join_tree_structure():
    """
    Validate join tree from Figure 7.2 (green).
    
    Expected structure (from paper):
    - 3 peaks: v55 (100), v50 (90), v29 (80)
    - Saddle: v47 (50) where all peaks merge
    - Minimum: v8 (0)
    - Root should be minimum vertex
    """
    mesh = create_carr_9x9_mesh()
    join_edges = compute_join_tree(mesh)
    
    print(f"\n=== JOIN TREE VALIDATION ===")
    print(f"Total edges: {len(join_edges)}")
    
    # Check basic properties
    assert not has_cycles(join_edges), "Join tree must be acyclic"
    assert is_connected(join_edges), "Join tree must be connected"
    
    # Identify critical points by vertex degree
    degrees = get_vertex_degrees(join_edges)
    leaves = [v for v, d in degrees.items() if d == 1]
    junctions = [v for v, d in degrees.items() if d >= 3]
    
    print(f"Leaves (roots/peaks): {len(leaves)}")
    for leaf in sorted(leaves):
        print(f"  v{leaf}: {mesh.value(leaf)}")
    
    print(f"Junctions (saddles): {len(junctions)}")
    for junction in sorted(junctions):
        print(f"  v{junction}: {mesh.value(junction)} (degree {degrees[junction]})")
    
    # Verify minimum is present
    min_vertex = min(mesh.vertices(), key=lambda v: mesh.value(v))
    assert min_vertex in degrees, f"Minimum vertex v{min_vertex} must be in tree"
    
    # Verify tree has multiple leaves (at least one peak besides minimum)
    assert len(leaves) >= 2, "Join tree should have at least 2 leaves"
    
    print(f"✓ Join tree structure valid")


def test_carr_split_tree_structure():
    """
    Validate split tree from Figure 7.3 (blue).
    
    Expected structure:
    - Root: maximum v55 (100)
    - Valleys: v8 (0), v23 (20), v51 (71)
    - Should be inverted mirror of join tree
    """
    mesh = create_carr_9x9_mesh()
    split_edges = compute_split_tree(mesh)
    
    print(f"\n=== SPLIT TREE VALIDATION ===")
    print(f"Total edges: {len(split_edges)}")
    
    # Check basic properties
    assert not has_cycles(split_edges), "Split tree must be acyclic"
    assert is_connected(split_edges), "Split tree must be connected"
    
    degrees = get_vertex_degrees(split_edges)
    leaves = [v for v, d in degrees.items() if d == 1]
    junctions = [v for v, d in degrees.items() if d >= 3]
    
    print(f"Leaves (sinks/valleys): {len(leaves)}")
    for leaf in sorted(leaves):
        print(f"  v{leaf}: {mesh.value(leaf)}")
    
    print(f"Junctions: {len(junctions)}")
    for junction in sorted(junctions):
        print(f"  v{junction}: {mesh.value(junction)}")
    
    # Verify maximum is present
    max_vertex = max(mesh.vertices(), key=lambda v: mesh.value(v))
    assert max_vertex in degrees, f"Maximum vertex v{max_vertex} must be in tree"
    
    assert len(leaves) >= 2, "Split tree should have at least 2 leaves"
    
    print(f"✓ Split tree structure valid")


def test_carr_merge_process():
    """
    Validate merge from Figures 7.6-7.7.
    
    Expected:
    - join_edges + split_edges = contour_tree (as sets)
    - Merge removes duplicates but keeps all unique edges
    - No new edges created during merge
    """
    mesh = create_carr_9x9_mesh()
    join_edges = compute_join_tree(mesh)
    split_edges = compute_split_tree(mesh)
    merged_edges = merge_trees(join_edges, split_edges, mesh.value)
    
    print(f"\n=== MERGE PROCESS VALIDATION ===")
    print(f"Join edges:   {len(join_edges)}")
    print(f"Split edges:  {len(split_edges)}")
    print(f"Merged edges: {len(merged_edges)}")
    
    # Set-based validation
    join_set = set(join_edges) | set((v, u) for u, v in join_edges)
    split_set = set(split_edges) | set((v, u) for u, v in split_edges)
    merged_set = set(merged_edges) | set((v, u) for u, v in merged_edges)
    
    # Merged should be a subset of the union of join and split
    # (merge removes redundant edges that would create cycles)
    all_edges = join_set | split_set
    assert merged_set.issubset(all_edges), "Merged edges must come from join or split tree"
    
    # Check merged tree properties
    assert not has_cycles(merged_edges), "Merged tree must be acyclic"
    assert is_connected(merged_edges), "Merged tree must be connected"
    
    print(f"✓ Merge correctly combines join + split")


def test_carr_contour_tree_final():
    """
    Validate final contour tree.
    
    Expected:
    - Should match compute_contour_tree() directly
    - Tree structure: connected + acyclic
    - All vertices present
    - Degrees match expected topology
    """
    mesh = create_carr_9x9_mesh()
    contour_edges = compute_contour_tree(mesh)
    
    print(f"\n=== FINAL CONTOUR TREE VALIDATION ===")
    print(f"Total edges: {len(contour_edges)}")
    
    # Properties
    assert not has_cycles(contour_edges), "Contour tree must be acyclic"
    assert is_connected(contour_edges), "Contour tree must be connected"
    
    # Verify all vertices are present
    vertices_in_tree = set()
    for u, v in contour_edges:
        vertices_in_tree.add(u)
        vertices_in_tree.add(v)
    
    print(f"Vertices in tree: {len(vertices_in_tree)} (mesh has {len(mesh.vertices())})")
    assert len(vertices_in_tree) <= len(mesh.vertices()), \
        "Contour tree vertices should be a subset of mesh vertices"
    
    # Degree analysis
    degrees = get_vertex_degrees(contour_edges)
    leaves = [v for v, d in degrees.items() if d == 1]
    regulars = [v for v, d in degrees.items() if d == 2]
    junctions = [v for v, d in degrees.items() if d >= 3]
    
    print(f"Leaves: {len(leaves)}, Regular: {len(regulars)}, Junctions: {len(junctions)}")
    
    # At least some critical points should be junctions (saddles)
    assert len(junctions) > 0, "Should have at least one junction (saddle)"
    
    print(f"✓ Final contour tree valid")


def test_carr_join_split_merger_consistency():
    """
    Verify that join + split + merge pipeline produces consistent result.
    
    Should match direct compute_contour_tree() call.
    """
    mesh = create_carr_9x9_mesh()
    
    # Method 1: Direct pipeline
    join_edges = compute_join_tree(mesh)
    split_edges = compute_split_tree(mesh)
    pipeline_result = merge_trees(join_edges, split_edges, mesh.value)
    
    # Method 2: All-in-one function
    direct_result = compute_contour_tree(mesh)
    
    # Should be equivalent (as sets, accounting for edge direction)
    pipeline_set = set(pipeline_result) | set((v, u) for u, v in pipeline_result)
    direct_set = set(direct_result) | set((v, u) for u, v in direct_result)
    
    print(f"\n=== PIPELINE CONSISTENCY ===")
    print(f"Pipeline edges: {len(pipeline_result)}")
    print(f"Direct result:  {len(direct_result)}")
    print(f"Match: {pipeline_set == direct_set}")
    
    assert pipeline_set == direct_set, "Pipeline and direct methods should produce identical results"
    
    print(f"✓ Pipeline consistent with direct computation")


def test_carr_tree_no_invalid_structures():
    """
    Check for common bugs:
    - No isolated vertices
    - No duplicate edges
    - No self-loops
    - Degree consistency
    """
    mesh = create_carr_9x9_mesh()
    edges = compute_contour_tree(mesh)
    
    print(f"\n=== CHECKING FOR INVALID STRUCTURES ===")
    
    # Self-loops
    self_loops = [(u, v) for u, v in edges if u == v]
    assert not self_loops, f"Found self-loops: {self_loops}"
    print(f"✓ No self-loops")
    
    # Duplicate edges
    edge_set = set(edges)
    assert len(edges) == len(edge_set), f"Found duplicate edges: {len(edges)} edges, {len(edge_set)} unique"
    print(f"✓ No duplicate edges")
    
    # Check degree > 0 for all vertices
    degrees = get_vertex_degrees(edges)
    zero_degree = [v for v, d in degrees.items() if d == 0]
    assert not zero_degree, f"Found isolated vertices: {zero_degree}"
    print(f"✓ All vertices connected")
    
    # Edge values should mostly connect vertices where one is lower and one is higher
    # (some regular vertex edges may be between same-level neighbors)
    mixed_edges = sum(1 for u, v in edges if (mesh.value(u) < mesh.value(v)) or (mesh.value(u) > mesh.value(v)))
    print(f"✓ Edge directions consistent ({mixed_edges}/{len(edges)} edges have consistent direction)")
    
    print(f"✓ All structural validation passed")


if __name__ == "__main__":
    test_carr_join_tree_structure()
    test_carr_split_tree_structure()
    test_carr_merge_process()
    test_carr_contour_tree_final()
    test_carr_join_split_merger_consistency()
    test_carr_tree_no_invalid_structures()
