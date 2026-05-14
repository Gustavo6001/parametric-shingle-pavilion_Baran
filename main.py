"""
Parametric Shingle Pavilion Generator

This is a beginner-friendly Python script that represents
the logic of a parametric Grasshopper-style pavilion.
"""

# -----------------------------
# Input Parameters
# -----------------------------

pavilion_span = 10.0
pavilion_height = 4.0
pavilion_length = 16.0

row_count = 12
column_count = 20

shingle_width = 0.8
shingle_height = 0.5
row_offset = 0.5
support_height = 0.2


# -----------------------------
# Functions
# -----------------------------

def create_base_arc(span, height):
    left_point = (-span / 2, 0, 0)
    top_point = (0, 0, height)
    right_point = (span / 2, 0, 0)

    arc_points = [left_point, top_point, right_point]

    return arc_points


def generate_grid(span, height, length, rows, columns):
    grid = []

    for row in range(rows):
        row_points = []

        for column in range(columns):
            x = -span / 2 + (span / (columns - 1)) * column
            y = -length / 2 + (length / (rows - 1)) * row

            normalized_x = abs(x) / (span / 2)
            z = height * (1 - normalized_x ** 2)

            row_points.append((x, y, z))

        grid.append(row_points)

    return grid


def apply_row_offset(grid, offset_value, shingle_width):
    offset_grid = []

    for row_index, row in enumerate(grid):
        new_row = []

        for point in row:
            x, y, z = point

            if row_index % 2 == 1:
                x = x + offset_value * shingle_width

            new_row.append((x, y, z))

        offset_grid.append(new_row)

    return offset_grid


def create_shingle(center_point, width, height, support_height):
    x, y, z = center_point

    lifted_z = z + support_height

    shingle = {
        "center": (x, y, lifted_z),
        "width": width,
        "height": height
    }

    return shingle


def generate_pavilion():
    arc = create_base_arc(pavilion_span, pavilion_height)

    grid = generate_grid(
        pavilion_span,
        pavilion_height,
        pavilion_length,
        row_count,
        column_count
    )

    offset_grid = apply_row_offset(
        grid,
        row_offset,
        shingle_width
    )

    shingles = []

    for row in offset_grid:
        for point in row:
            shingle = create_shingle(
                point,
                shingle_width,
                shingle_height,
                support_height
            )

            shingles.append(shingle)

    return arc, offset_grid, shingles


# -----------------------------
# Run the Program
# -----------------------------

arc, grid, shingles = generate_pavilion()

print("Parametric Shingle Pavilion Generated")
print("------------------------------------")
print("Pavilion span:", pavilion_span)
print("Pavilion height:", pavilion_height)
print("Pavilion length:", pavilion_length)
print("Rows:", row_count)
print("Columns:", column_count)
print("Total shingles:", len(shingles))