"""
- Detects cycle in graph
- Checks network connectivity
- MST (Kruskals Algorithm)
- efficiently manages disjoint sets
- quickly determines if two elements are in the same set
- quickly merge two elements into the same set

"""
class UnionFind:
    """
    Basic Union-Find (Disjoint Set) structure.

    Implements:
        make_set(x)
        find(x)
        union(a, b)

    This version is intentionally simple so we can
    incrementally add optimisations from Tarjan (1975).
    """

    def __init__(self):
        self.parent = {}
        self.size = {}

    def make_set(self, x):
        """
        Create a new set containing element x.
        """
        self.parent[x] = x
        self.size[x] = 1

    def find(self, x):
        """
        Find the root (representative) of the set containing x.
        """
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union(self, a, b):
        """
        Merge sets containing a and b.
        """
        rootA = self.find(a)
        rootB = self.find(b)

        if rootA == rootB:
            return

        # simple attach
        self.parent[rootB] = rootA
        self.size[rootA] += self.size[rootB]


uf = UnionFind()

for i in range(5):
    uf.make_set(i)

uf.union(0,1)
uf.union(1,2)

print(uf.find(2))
print(uf.find(0))