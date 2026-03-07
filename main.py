from src.meshes.mesh2d import TriMesh2D

if __name__ == "__main__":
    values = {
        0: 0.1,
        1: 0.7,
        2: 0.2,
        3: 0.9,
    }

    triangles = [
        (0,1,3),
        (0,3,2),
    ]

    mesh = TriMesh2D(values,triangles)

    if __name__ == "__main__":
        print("Creating a simple 2D triangulated mesh...\n")

        # Vertex scalar values
        values = {
            0: 0.1,
            1: 0.7,
            2: 0.2,
            3: 0.9,
        }

        # Triangle connectivity
        # Square split into two triangles
        #
        # 2 ---- 3
        # |   /  |
        # |  /   |
        # 0 ---- 1
        #
        triangles = [
            (0, 1, 3),
            (0, 3, 2),
        ]

        mesh = TriMesh2D(values, triangles)

        print("Vertices in mesh:")
        print(mesh.vertices())

        print("\nScalar values:")
        for v in mesh.vertices():
            print(f"  vertex {v} -> f(v) = {mesh.value(v)}")

        print("\nTriangles in mesh:")
        for tri in mesh.triangles():
            print(f"  {tri}")

        print("\nSorted vertices (ascending by value):")
        print(mesh.sorted_vertices())

        print("\nSorted vertices (descending by value):")
        print(mesh.sorted_vertices(ascending=False))