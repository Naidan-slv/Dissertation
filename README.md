### Goal for this Sprint
Implement the contour tree pipeline by building and testing the sub-algorithms in order:

1. **Algorithm 7.2** (Join sweep) → produces **Join Tree**
2. **Algorithm 7.2 again (Split sweep)** → produces **Split Tree**
3. **Algorithm 7.3** (Merge join + split) → produces **Contour Tree**
4. **Optional**: Algorithm 7.4 reduction → produces **Unaugmented Contour Tree**

I will begin with a tiny synthetic mesh where I can predict the result by hand.

---
## Implementation for now : 

### Step 1 — Mesh representation (no external libs)
Implement a minimal `Mesh` that stores:
- `values: dict[int, float]`
- `edges: list[tuple[int,int]]`
- builds `adj: dict[int, list[int]]`
- provides `vertices`
---

### Step 2 — One tiny synthetic test mesh (hand-made)
Create a tiny dataset where join behaviour is obvious and can be computed on paper.

Recommended first test: **two peaks merging at one join**
- Values: `80` and `70` are separate peaks
- They merge at `50`
- Everything drains to `0`

Example structure:
- Vertices: `A=80`, `B=70`, `C=50`, `D=0`
- Edges: `A—C`, `B—C`, `C—D`

Done when:
- It builds a `Mesh` without errors
- I can draw it on paper and predict where the join occurs
---

### Step 3 — Union–Find (Disjoint Set Union)
Implement `UnionFind` with:
- `find(x)` with path compression
- `union(a,b)` with union by rank/size

**Extra requirement for Algorithm 7.2**:
Track the “lowest vertex” in each component so we can do:
> “Let u be the lowest vertex in component Comp(n)”

Implementation idea:
- maintain `comp_low[root] = vertex_id_with_lowest_f_in_component`
- update `comp_low` during union

Done when:
- after unions, `find(a) == find(b)` if connected
- `comp_low[find(x)]` returns the lowest-valued vertex in the component

---

### Step 4 — Implement Join Sweep (Algorithm 7.2) ONLY


After this we can work on creating multiple tests for each case to make sure it works

