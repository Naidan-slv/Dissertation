from src.meshes.mesh2d import TriMesh2D

if __name__ == "__main__":
    values = {
        0: 0.1,
        1: 0.7,
        2: 0.2,
        3: 0.9,
    }

    mesh = TriMesh2D(values)

    print("Vertices:", mesh.vertices())
    for v in mesh.vertices():
        print(f"value({v}) = {mesh.value(v)}")


    print("Sorted ascending based off scalar value:", mesh.sorted_vertices())
    print("Sorted descending based off scalar value:", mesh.sorted_vertices(ascending=False))