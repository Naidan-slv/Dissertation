class TwoDimensionalMesh:

    def __init__(self, values: dict[int, float], edges: list[tuple[int, int]]):
        self.values = values
        self.edges = edges
        self.nodes = set(values.keys())

        # Build adjacency list
        self.adjacent_nodes = {v: [] for v in self.nodes}

        for u, v in edges:
            if u not in self.nodes or v not in self.nodes:
                raise ValueError("Edge contains vertex not in values dictionary")

            self.adjacent_nodes[u].append(v)
            self.adjacent_nodes[v].append(u)

    def get_vertices(self):
        return list(self.nodes)

    def get_neighbors(self, v: int):
        return self.adjacent_nodes[v]

    def get_value(self, v: int):
        return self.values[v]

    def sorted_vertices(self, descending: bool = True):
        return sorted(self.nodes, key=self.get_value, reverse=descending)

    def __repr__(self):
        return f"TwoDimensionalMesh(num_vertices={len(self.nodes)}, num_edges={len(self.edges)})"
