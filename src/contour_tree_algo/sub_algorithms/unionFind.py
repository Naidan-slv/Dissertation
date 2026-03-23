"""
Union-Find (Disjoint Set Union)

Extended for use in contour tree construction.

Standard Union-Find operations:
- make_set(x, value)
- find(x)
- union(a, b)

Extended for Carr et al. join/split sweep:
- lowest_in_component(x)   -- for join sweep (Algorithm 4.1 ascending)
- highest_in_component(x)  -- for split sweep (Algorithm 4.1 descending)

Based on:
- Tarjan, R.E. (1975). "Efficiency of a Good But Not Linear Set Union Algorithm."
  Journal of the ACM, 22(2), 215-225.
  → Provides the weighted union rule and find() structure.

- Carr, H., Snoeyink, J., Axen, U. (2003).
  "Computing Contour Trees in All Dimensions."
  Computational Geometry, 24(3), 75-94.
  → Algorithm 4.1 requires LowestVertex tracking per component.
  → This is the 'comp_low' dictionary below.
"""


class UnionFind:
    """
    Union-Find (Disjoint Set) structure extended for contour tree construction.

    Each element represents a vertex in a mesh with a scalar value f(v).

    Supports:
        make_set(x, value)         -- create singleton set for vertex x
        find(x)                    -- return root of component containing x
        union(a, b)                -- merge components of a and b
        lowest_in_component(x)     -- return vertex with lowest f(v) in component
        highest_in_component(x)    -- return vertex with highest f(v) in component

    Based on:
        Tarjan (1975) -- weighted union rule
        Carr et al. (2003) -- LowestVertex extension for Algorithm 4.1
    """

    def __init__(self):
        # -----------------------------------------
        # Internal state
        # Based on: Tarjan (1975)
        # -----------------------------------------

        # parent[x] = the parent of x in the Union-Find forest
        # if parent[x] == x, then x is the root of its component
        self.parent = {}

        # size[root] = number of elements in the component rooted at root
        # used for the weighted union rule (always attach smaller under larger)
        self.size = {}

        # -----------------------------------------
        # Extension for Carr et al. (2003) Algorithm 4.1
        # -----------------------------------------

        # comp_low[root] = the vertex with the LOWEST scalar value
        # in the component rooted at root.
        # This is the 'LowestVertex' array described in Carr et al. (2003).
        self.comp_low = {}

        # comp_high[root] = the vertex with the HIGHEST scalar value
        # in the component rooted at root.
        # Dual of comp_low, used for split sweep (descending).
        # Carr et al. Algorithm 4.1 applied in reverse.
        self.comp_high = {}

        # scalar values for each vertex — needed to compare during union
        self.value = {}

    # -----------------------------------------
    # Step 1 — Create singleton set
    # Based on: Tarjan (1975), make_set operation
    # Extended by: Carr et al. (2003) to store scalar value and LowestVertex
    # -----------------------------------------

    def make_set(self, x, scalar_value):
        """
        Create a new singleton set containing only vertex x.

        Args:
            x:             vertex ID (integer)
            scalar_value:  the scalar value f(x) at this vertex
        """
        # x starts as its own parent (singleton component)
        self.parent[x] = x

        # singleton component has size 1
        self.size[x] = 1

        # store the scalar value so we can compare during union
        self.value[x] = scalar_value

        # the lowest vertex in a singleton is x itself
        # (Carr et al. 2003: LowestVertex[i] := yi)
        self.comp_low[x] = x

        # the highest vertex in a singleton is also x itself
        # (Dual of comp_low for split sweep)
        self.comp_high[x] = x

    # -----------------------------------------
    # Step 2 — Find root of component
    # Based on: Tarjan (1975), FIND operation
    # This version uses simple traversal (no path compression)
    # to keep the algorithm transparent and traceable.
    # -----------------------------------------

    def find(self, x):
        """
        Find and return the root (representative) of the component containing x.

        Follows parent pointers until we reach a root (where parent[x] == x).

        Args:
            x: vertex ID

        Returns:
            root vertex ID of the component containing x
        """
        # walk up the parent chain until we reach the root
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    # -----------------------------------------
    # Step 3 — Merge two components
    # Based on: Tarjan (1975), weighted union rule
    # Extended by: Carr et al. (2003) to maintain LowestVertex after merge
    # -----------------------------------------

    def union(self, a, b):
        """
        Merge the components containing a and b.

        Uses the weighted union rule (Tarjan 1975):
            always attach the smaller component under the larger one.
            Tie-break by scalar value (higher value becomes root for split efficiency).

        Also updates comp_low (Carr et al. 2003):
            after merging, the new component's lowest vertex is the
            lower of the two components' lowest vertices.

        Args:
            a, b: vertex IDs to merge

        Returns:
            root of the merged component
        """
        rootA = self.find(a)
        rootB = self.find(b)

        if rootA == rootB:
            return rootA

        if self.size[rootA] < self.size[rootB]:
            rootA, rootB = rootB, rootA
        elif self.size[rootA] == self.size[rootB]:
            if self.value[rootB] > self.value[rootA]:
                rootA, rootB = rootB, rootA

        self.parent[rootB] = rootA
        self.size[rootA] += self.size[rootB]

        # -----------------------------------------
        # Update LowestVertex after merge (Carr et al. 2003)
        # The new lowest vertex is whichever of the two roots
        # has the lower scalar value.
        # -----------------------------------------
        low_a = self.comp_low[rootA]
        low_b = self.comp_low[rootB]

        if self.value[low_a] <= self.value[low_b]:
            self.comp_low[rootA] = low_a
        else:
            self.comp_low[rootA] = low_b

        # -----------------------------------------
        # Update HighestVertex after merge (dual for split sweep)
        # The new highest vertex is whichever of the two roots
        # has the higher scalar value.
        # -----------------------------------------
        high_a = self.comp_high[rootA]
        high_b = self.comp_high[rootB]

        if self.value[high_a] >= self.value[high_b]:
            self.comp_high[rootA] = high_a
        else:
            self.comp_high[rootA] = high_b

        return rootA

    # -----------------------------------------
    # Step 4 — Query lowest vertex in component
    # Based on: Carr et al. (2003), Algorithm 4.1
    # "LowestVertex[Component[j]]"
    # -----------------------------------------

    def lowest_in_component(self, x):
        """
        Return the vertex with the lowest scalar value in the component
        containing x.

        This is the 'LowestVertex' lookup described in Carr et al. (2003)
        Algorithm 4.1, used during the join sweep to determine which
        join tree edge to add.

        Args:
            x: vertex ID

        Returns:
            vertex ID of the lowest-valued vertex in x's component
        """
        root = self.find(x)
        return self.comp_low[root]

    # -----------------------------------------
    # Step 5 — Query highest vertex in component
    # Based on: Carr et al. (2003), Algorithm 4.1 applied in reverse
    # Used for split sweep (descending)
    # -----------------------------------------

    def highest_in_component(self, x):
        """
        Return the vertex with the highest scalar value in the component
        containing x.

        Args:
            x: vertex ID

        Returns:
            vertex ID of the highest-valued vertex in x's component
        """
        root = self.find(x)
        return self.comp_high[root]