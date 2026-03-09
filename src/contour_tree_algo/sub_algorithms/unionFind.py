"""
Union-Find (Disjoint Set Union)

Uses:
- Detect cycle in graph
- Check network connectivity
- Kruskal's MST algorithm
- Efficiently manage disjoint sets
- Quickly determine if two elements are in the same set
- Quickly merge two sets into one

Current increment:
- Add weighted union rule (union by size)

Based on:
- Tarjan (1975), weighted union rule
"""

class UnionFind:
    """
    Basic Union-Find (Disjoint Set) structure.

    Implements:
        make_set(x)
        find(x)
        union(a, b)

    This version adds the weighted union rule:
    always attach the smaller tree under the larger tree.
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
        Merge the sets containing a and b using union by size.
        """
        rootA = self.find(a)
        rootB = self.find(b)

        if rootA == rootB:
            return rootA

        # Weighted union rule:
        # attach the smaller tree under the larger tree
        if self.size[rootA] < self.size[rootB]:
            rootA, rootB = rootB, rootA

        self.parent[rootB] = rootA
        self.size[rootA] += self.size[rootB]

        return rootA


if __name__ == "__main__":
    uf = UnionFind()

    for i in range(5):
        uf.make_set(i)

    uf.union(0, 1)
    uf.union(1, 2)
    uf.union(3, 4)
    uf.union(2, 4)

    print("Root of 0:", uf.find(0))
    print("Root of 2:", uf.find(2))
    print("Root of 4:", uf.find(4))

    print("Parent map:", uf.parent)
    print("Size map:", uf.size)