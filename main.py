# Student Name: Baran Koç
# Project: Parametric Curved Shingle Pavilion

import Rhino.Geometry as rg
import math

# ==========================================
# INPUT TYPE CONVERSION
# ==========================================

Height = float(Height)
Base_width = float(Base_width)
depth = float(depth)
curvature_points = float(curvature_points)

rows = int(rows)
columns = int(columns)

panel_width = float(panel_width)
panel_height = float(panel_height)
panel_thickness = float(panel_thickness)
panel_curvature = float(panel_curvature)
panel_rotation = float(panel_rotation)

min_rotation = float(min_rotation)
max_rotation = float(max_rotation)

min_offset = float(min_offset)
max_offset = float(max_offset)

frame_thickness = float(frame_thickness)
rib_spacing = float(rib_spacing)
purlin_spacing = float(purlin_spacing)

if attractor_point is None:
    attractor_point = rg.Point3d(0, depth / 2.0, Height / 2.0)

# ==========================================
# OUTPUT CONTAINERS
# ==========================================

uv_grid = []
surface_frames = []
ribs = []
purlins = []
repeated_panels = []
attractor_rotation = []
final_pavilion = []

section_curve = None
mirrored_curve = None
main_surface = None
single_panel = None

# ==========================================
# CREATE BASE PROFILE CURVES
# ==========================================

pts_left = []
pts_right = []

for i in range(rows + 1):
    t = float(i) / rows

    z = t * Height
    curve_factor = math.sin(t * math.pi) * curvature_points * Base_width

    x_left = -Base_width / 2.0 + curve_factor
    x_right = Base_width / 2.0 - curve_factor

    pts_left.append(rg.Point3d(x_left, 0, z))
    pts_right.append(rg.Point3d(x_right, 0, z))

section_curve = rg.Curve.CreateInterpolatedCurve(pts_left, 3)
mirrored_curve = rg.Curve.CreateInterpolatedCurve(pts_right, 3)

# ==========================================
# CREATE MAIN SURFACE
# ==========================================

loft = rg.Brep.CreateFromLoft(
    [section_curve, mirrored_curve],
    rg.Point3d.Unset,
    rg.Point3d.Unset,
    rg.LoftType.Normal,
    False
)

if loft and len(loft) > 0:
    main_surface = loft[0]

# ==========================================
# DIVIDE SURFACE
# ==========================================

if main_surface:
    face = main_surface.Faces[0]

    u_domain = face.Domain(0)
    v_domain = face.Domain(1)

    for i in range(rows):
        for j in range(columns):

            u = u_domain.ParameterAt(float(i) / max(rows - 1, 1))
            v = v_domain.ParameterAt(float(j) / max(columns - 1, 1))

            pt = face.PointAt(u, v)
            normal = face.NormalAt(u, v)
            normal.Unitize()

            plane = rg.Plane(pt, normal)

            uv_grid.append(pt)
            surface_frames.append(plane)

# ==========================================
# CREATE RIBS
# ==========================================

rib_count = max(2, int(depth / rib_spacing) + 1)

for r in range(rib_count):
    y = float(r) / (rib_count - 1) * depth

    for crv in [section_curve, mirrored_curve]:
        c = crv.DuplicateCurve()
        c.Transform(rg.Transform.Translation(0, y, 0))

        pipe = rg.Brep.CreatePipe(
            c,
            frame_thickness,
            False,
            rg.PipeCapMode.Flat,
            True,
            0.01,
            0.01
        )

        if pipe:
            ribs.extend(pipe)

# ==========================================
# CREATE PURLINS
# ==========================================

purlin_count = max(2, int(Height / purlin_spacing) + 1)

for i in range(purlin_count):
    t = float(i) / (purlin_count - 1)

    z = t * Height
    curve_factor = math.sin(t * math.pi) * curvature_points * Base_width

    x_left = -Base_width / 2.0 + curve_factor
    x_right = Base_width / 2.0 - curve_factor

    start_pt = rg.Point3d(x_left, 0, z)
    end_pt = rg.Point3d(x_right, depth, z)

    line = rg.Line(start_pt, end_pt)

    pipe = rg.Brep.CreatePipe(
        line.ToNurbsCurve(),
        frame_thickness * 0.6,
        False,
        rg.PipeCapMode.Flat,
        True,
        0.01,
        0.01
    )

    if pipe:
        purlins.extend(pipe)

# ==========================================
# CREATE PANEL FUNCTION
# ==========================================

def create_panel(base_plane, rotation_value, offset_value):
    plane = rg.Plane(base_plane)

    # Move panel outward along surface normal
    plane.Origin += plane.ZAxis * offset_value

    # Create rectangular panel
    rect = rg.Rectangle3d(
        plane,
        rg.Interval(-panel_width / 2.0, panel_width / 2.0),
        rg.Interval(-panel_height / 2.0, panel_height / 2.0)
    )

    # Create planar Brep
    breps = rg.Brep.CreatePlanarBreps(rect.ToNurbsCurve())

    if not breps or len(breps) == 0:
        return None

    brep = breps[0]

    # Rotate panel
    center = plane.Origin

    rot = rg.Transform.Rotation(
        math.radians(rotation_value),
        plane.XAxis,
        center
    )

    brep.Transform(rot)

    return brep

# ==========================================
# ATTRACTOR + PANEL DISTRIBUTION
# ==========================================

max_distance = math.sqrt(
    Base_width ** 2 +
    depth ** 2 +
    Height ** 2
)

for index, plane in enumerate(surface_frames):

    pt = plane.Origin
    distance = pt.DistanceTo(attractor_point)

    factor = 1.0 - min(distance / max_distance, 1.0)

    rotation_value = (
        min_rotation +
        factor * (max_rotation - min_rotation)
    )

    offset_value = (
        min_offset +
        factor * (max_offset - min_offset)
    )

    row = index // columns

    local_plane = rg.Plane(plane)

    # Shift every second row
    if row % 2 == 1:
        local_plane.Origin += local_plane.XAxis * (panel_width * 0.5)

    panel = create_panel(
        local_plane,
        rotation_value,
        offset_value
    )

    if panel:
        repeated_panels.append(panel)
        attractor_rotation.append(rotation_value)

# ==========================================
# SINGLE PANEL OUTPUT
# ==========================================

if surface_frames:
    single_panel = create_panel(
        surface_frames[0],
        panel_rotation,
        min_offset
    )

# ==========================================
# FINAL ASSEMBLY
# ==========================================

if main_surface:
    final_pavilion.append(main_surface)

final_pavilion.extend(ribs)
final_pavilion.extend(purlins)
final_pavilion.extend(repeated_panels)