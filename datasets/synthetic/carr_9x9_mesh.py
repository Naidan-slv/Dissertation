"""
9×9 grid from Carr et al. (2003) paper.

Critical points: 0 (min), 20, 71, 80, 90, 100 (max)
Used to validate join/split tree computation against paper's expected output.
"""

from src.meshes.grid_mesh import GridMesh


def create_carr_9x9_mesh():
    """
    Create the 9×9 grid mesh from Carr et al. (2003) Figures 7.2-7.5.
    
    Vertex layout (row-major, bottom to top):
    Row 7:  29  37  39  70  74  84  38  36  26
    Row 6:  27 100  49  72  85  89  83  28  24
    Row 5:  25  47  50  73  86  90  71  82  22
    Row 4:  23  75  79  48  69  87  88  81  18
    Row 3:  19  76  80  78  46  68  67  40  16
    Row 2:  17  41  77  45  35  20  21  32  15
    Row 1:  13  42  43  44  34  33  31  30  14
    Row 0:  12  11  10   9   8   7   6   5   0
    
    81 vertices total. Vertex ID = row*9 + col.
    """
    grid_values = [
        [12, 11, 10,  9,  8,  7,  6,  5,  0],
        [13, 42, 43, 44, 34, 33, 31, 30, 14],
        [17, 41, 77, 45, 35, 20, 21, 32, 15],
        [19, 76, 80, 78, 46, 68, 67, 40, 16],
        [23, 75, 79, 48, 69, 87, 88, 81, 18],
        [25, 47, 50, 73, 86, 90, 71, 82, 22],
        [27,100, 49, 72, 85, 89, 83, 28, 24],
        [29, 37, 39, 70, 74, 84, 38, 36, 26],
    ]
    
    values = {}
    for row in range(8):
        for col in range(9):
            v_id = row * 9 + col
            values[v_id] = grid_values[row][col]
    
    edges = []
    
    for row in range(8):
        for col in range(9):
            v_id = row * 9 + col
            
            if col < 8:
                edges.append((v_id, v_id + 1))
            if row < 7:
                edges.append((v_id, v_id + 9))
            if row < 7 and col > 0:
                edges.append((v_id, v_id + 8))
            if row < 7 and col < 8:
                edges.append((v_id, v_id + 10))
    
    mesh = GridMesh(9, 8, values, edges)
    return mesh
