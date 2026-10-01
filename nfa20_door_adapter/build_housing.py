#!/usr/bin/env python3
"""
NF-A20 external door housing (v3, round): plinth clamped to the cutout with a
collar + inner ring, cylindrical skirt, spoke grille, magnetic mesh bezel.
Everything stays inside the acrylic window's edge (r 114.7) except the fan's
own corners, which poke out through windows in the skirt.

Frame of reference (all parts are modelled here, then flipped for printing):
  origin  = centre of the door's round cutout
  x right, y up, AS SEEN FROM OUTSIDE THE CASE
  z       = 0 at the steel's outer face, +z away from the case

Stack (z, mm):  -9.4 .. -0.9 inner ring (inside the case), collar through the cutout
                   0 .. 14   plinth, round r 90.7..114, bears on steel r 90.7..112.5
                  14 .. 44   NF-A20, exhaust face on the plinth, intake outward
                14.5 .. 44   skirt, r 111..114, with 4 windows for the fan corners
                  44 .. 49   front plate r 95..117 with spoke grille
                  49 .. 49.3 mesh
                49.3 .. 52.8 magnetic bezel r 92..117

Fixings: 4 x M5 x 20 from inside (inner ring -> door -> nut in plinth)
         4 x M4 x 40 from the front (plate -> fan corner -> plinth), thread-forming
         16 x 6x2 magnets, 1 mesh ~ 240 mm round or 235 square

Parts (print counts):
  flange_sector     x4   pinwheel 90 deg sectors of the plinth, with the collar
  inner_ring_sector x4   backing ring inside the case
  housing_quadrant  x4   skirt quadrant + quarter of the front plate and grille
  bezel_sector      x4   pinwheel arcs, clamp the mesh, 8 magnet pairs

Run:  python3 build_housing.py     -> stl_v2/*.stl, plan_v2.png
"""
import math
import os
import sys

import numpy as np
from manifold3d import CrossSection, Manifold

# ------------------------------------------------------------ door (measured)
DOOR_BCD = 208.0          # 8 holes at 0/45/90.. deg (measured 207.7)
CUTOUT_D = 187.0
STEEL_T = 0.86
ACRYLIC_EDGE_R = 114.7    # inner edge of the acrylic window, from photo fit
ACRYLIC_PROUD = 3.3
CAPNUT_R = 125.0          # acrylic fasteners sit on this radius (photo fit)
CAPNUT_ANGLES = (96, 44, 0, -45, -96)   # outside view, deg

# ------------------------------------------------------------------- fan
FAN_W = 200.0
FAN_T = 30.0
FAN_PITCH = 154.0
FAN_HOLE_XY = FAN_PITCH / 2            # 77, 77 -> r 108.9 at 45 deg
FAN_OPEN_R = 95.0
FAN_CORNER_R = 8.0

# ------------------------------------------------------------- plinth ring
Z_FLANGE = 14.0           # thickness; fan back face sits here
R_IN = 90.7               # bore through plinth and collar
R_OUT = ACRYLIC_EDGE_R - 0.7           # 114: sits just inside the acrylic edge
R_MID = 103.0             # radius of the lap step between inner/outer bands
LAP_HALF = 5.0            # deg: tongue length each side of the nominal seam
SEAM_GAP = 0.25           # total clearance at every mating face
R_BEAR = 112.5            # door-face contact ends here; relieved beyond
RELIEF_DEPTH = 4.5        # safety against the acrylic step if the edge is closer than measured
# collar through the cutout, gripped by the inner ring
COLLAR_OD = 185.8         # 0.6 mm radial clearance to a 187 mm hole; tune after a test print
COLLAR_CHAMFER = 0.8
# door screws: M5 from INSIDE the case into a hex nut captured on the fan face
DOOR_SCREW_D = 5.5
DOOR_SLOT_PLAY = 1.0
NUT_AF = 8.0 + 0.3
NUT_POCKET_DEPTH = 6.0
# fan screws: M4 x 40 from the front, through the fan, into the plinth
FAN_SCREW_TAP_D = 3.6     # thread-forming hole for M4 (use FAN_INSERT for heat-set inserts)
FAN_SCREW_HOLE_DEPTH = 12.0
FAN_INSERT = False        # True -> 5.6 x 8 mm pocket for an M4 heat-set insert instead
FAN_INSERT_D = 5.6
FAN_INSERT_H = 8.0
# inner backing ring (inside the case)
INNER_T = 8.0
INNER_R_IN = COLLAR_OD / 2 + 0.25
INNER_R_OUT = 117.0
INNER_R_BEAR = 113.0      # inside face has near-flush acrylic screw heads at r 119-128
INNER_RELIEF = 1.5
INNER_CBORE_D = 9.5
INNER_CBORE_DEPTH = 4.0
COLLAR_H = STEEL_T + INNER_T + 0.5

# ------------------------------------------------------------------ housing
WALL = 3.0
SKIRT_R_OUT = R_OUT                        # 114, flush with the plinth
SKIRT_R_IN = SKIRT_R_OUT - WALL            # 111
Z_SKIRT_BOTTOM = Z_FLANGE + 0.5            # sits on the plinth, 0.5 mm reveal
Z_FAN_TOP = Z_FLANGE + FAN_T               # 44
PLATE_T = 5.0
Z_PLATE_TOP = Z_FAN_TOP + PLATE_T          # 49
PLATE_R = 117.0                            # 3 mm lip over the skirt, room for the screw heads
PLATE_OPEN_R = 95.0
FAN_SCREW_D = 4.5                          # M4 clearance through plate
FAN_SCREW_HEAD_D = 7.6                     # M4 socket head 7.0 + clearance
FRONT_CBORE_DEPTH = 2.5
GRILLE_T = 3.0
GRILLE_RINGS = (28.0, 50.0, 72.0)
GRILLE_BAR = 3.0
GRILLE_SPOKES = 16                          # every 22.5 deg, includes the axes
WALL_LAP_DEG = 3.0                          # wall lap tongue, deg (~6 mm at r 112)
TONGUE_TOP_GAP = 0.3                        # tongue tops sit this far below the neighbour's plate
WINDOW_CLEAR_DEG = 1.5                      # extra on each side of the fan corner windows
TIE_SLOT = (4.0, 3.0)                       # along wall, along z
TIE_SLOT_ANGLES = (14.0, 19.0)              # deg from the quadrant start, beside each window
TIE_SLOT_Z = 22.0

# -------------------------------------------------------------------- bezel
MESH_T = 0.3
BEZEL_T = 3.5
BEZEL_R = PLATE_R
BEZEL_OPEN_R = 92.0
MAGNET_D = 6.0 + 0.4
MAGNET_H = 2.0 + 0.2
MAGNET_R = 100.0
MAGNET_ANGLES = (5.0, 40.0)                 # per quadrant, +90k -> 8 magnets
BEZEL_A0 = 11.25                            # bezel seams 11.25 deg off the housing seams

SEG = 256
HOLE_SEG = 48
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl_v2")


# ------------------------------------------------------------------ helpers
def rad(a):
    return math.radians(a)


def ann_sector(r1, r2, a0, a1, h, z0=0.0):
    if a1 - a0 >= 360:
        a0, a1 = 0.0, 360.0
    n = max(4, int(SEG * (a1 - a0) / 360.0))
    outer = [(r2 * math.cos(rad(a0 + (a1 - a0) * i / n)),
              r2 * math.sin(rad(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    inner = [(r1 * math.cos(rad(a1 - (a1 - a0) * i / n)),
              r1 * math.sin(rad(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    return CrossSection([outer + inner]).extrude(h).translate([0, 0, z0])


def cyl(d, h, x=0.0, y=0.0, z=0.0, seg=HOLE_SEG):
    return Manifold.cylinder(h, d / 2, d / 2, seg).translate([x, y, z])


def hexp(af, h, x=0.0, y=0.0, z=0.0):
    r = af / math.sqrt(3)
    return Manifold.cylinder(h, r, r, 6).translate([x, y, z])


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def radial_slot(maker, r_c, ang, play):
    a = rad(ang)
    m1 = maker((r_c - play) * math.cos(a), (r_c - play) * math.sin(a))
    m2 = maker((r_c + play) * math.cos(a), (r_c + play) * math.sin(a))
    return (m1 + m2).hull()


def deg_at(r, mm):
    """Angle in degrees subtended by an arc of `mm` at radius r."""
    return math.degrees(mm / r)


def lapped_sector(r_in, r_out, r_mid, a0, a1, lap, gap, h, z0=0.0):
    """
    One sector of a ring split with staggered radial laps, as a SINGLE solid.
    Nominal span a0..a1.  The inner band (r_in..r_mid) is shifted by -lap, the
    outer band (r_mid..r_out) by +lap, so adjacent sectors interlock.  The two
    bands overlap radially inside the body; only the tongues are trimmed back
    to r_mid -/+ gap/2 so mating sectors don't touch.  Every mating face gets
    gap/2 of clearance.
    """
    g_in = deg_at(r_in, gap / 2)
    g_out = deg_at(r_out, gap / 2)
    g_mid = deg_at(r_mid, gap / 2)
    inner = ann_sector(r_in, r_mid + 1.0, a0 - lap + g_in, a1 - lap - g_in, h, z0)
    outer = ann_sector(r_mid - 1.0, r_out, a0 + lap + g_out, a1 + lap - g_out, h, z0)
    # trim the inner tongue (a0-lap .. a0+lap) back to r_mid - gap/2
    inner -= ann_sector(r_mid - gap / 2, r_mid + 2.0, a0 - lap - 1.0, a0 + lap + g_mid, h + 2, z0 - 1)
    # trim the outer tongue (a1-lap .. a1+lap) back to r_mid + gap/2
    outer -= ann_sector(r_mid - 2.0, r_mid + gap / 2, a1 - lap - g_mid, a1 + lap + 1.0, h + 2, z0 - 1)
    return inner + outer


def to_trimesh(m):
    import trimesh
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    f = np.asarray(mesh.tri_verts)
    return trimesh.Trimesh(v, f, process=False)


# ------------------------------------------------------------- plinth ring
def flange_sector(k=0):
    """Pinwheel sector: door screw at 0 deg, fan screw at 45 deg."""
    a0, a1 = -22.5, 67.5
    body = lapped_sector(R_IN, R_OUT, R_MID, a0, a1, LAP_HALF, SEAM_GAP, Z_FLANGE)
    # collar: follows the inner band's span so the seams line up
    r_co = COLLAR_OD / 2
    g_in = deg_at(R_IN, SEAM_GAP / 2)
    collar = ann_sector(R_IN, r_co, a0 - LAP_HALF + g_in, a1 - LAP_HALF - g_in,
                        COLLAR_H + 0.5, -COLLAR_H)
    # 45 deg cone, extended 0.1 beyond both ends of the cutter disc so no full slice is removed
    cone = Manifold.cylinder(COLLAR_CHAMFER + 0.2, r_co - COLLAR_CHAMFER - 0.1, r_co + 0.1, SEG) \
        .translate([0, 0, -COLLAR_H - 0.1])
    cham = cyl(2 * r_co + 2, COLLAR_CHAMFER + 0.01, 0, 0, -COLLAR_H - 0.01, seg=SEG) - cone
    body = (body + collar) - cham
    r_door = DOOR_BCD / 2
    # M5 from inside: through slot + captive nut pocket on the fan face (z = top)
    body -= radial_slot(lambda x, y: cyl(DOOR_SCREW_D, Z_FLANGE + 2, x, y, -1),
                        r_door, 0, DOOR_SLOT_PLAY)
    body -= radial_slot(lambda x, y: hexp(NUT_AF, NUT_POCKET_DEPTH + 1, x, y,
                                          Z_FLANGE - NUT_POCKET_DEPTH),
                        r_door, 0, DOOR_SLOT_PLAY)
    # M4 fan screw from the front: blind hole (or insert pocket) in the fan face
    if FAN_INSERT:
        body -= cyl(FAN_INSERT_D, FAN_INSERT_H + 1, FAN_HOLE_XY, FAN_HOLE_XY, Z_FLANGE - FAN_INSERT_H)
        body -= cyl(FAN_SCREW_TAP_D + 0.6, FAN_SCREW_HOLE_DEPTH + 1, FAN_HOLE_XY, FAN_HOLE_XY,
                    Z_FLANGE - FAN_SCREW_HOLE_DEPTH)
    else:
        body -= cyl(FAN_SCREW_TAP_D, FAN_SCREW_HOLE_DEPTH + 1, FAN_HOLE_XY, FAN_HOLE_XY,
                    Z_FLANGE - FAN_SCREW_HOLE_DEPTH)
    # door-face relief beyond the bearing radius
    body -= ann_sector(R_BEAR, R_OUT + 1, a0 - 20, a1 + 20, RELIEF_DEPTH + 1, -1)
    return body.rotate([0, 0, 90 * k]) if k else body


# ------------------------------------------------------------- inner ring
def inner_ring_sector(k=0):
    """Backing ring inside the case, bolt at 0 deg, seams on the diagonals."""
    a0, a1 = -45.0, 45.0
    z0 = -STEEL_T - INNER_T
    body = lapped_sector(INNER_R_IN, INNER_R_OUT, R_MID, a0, a1, LAP_HALF, SEAM_GAP, INNER_T, z0)
    r_door = DOOR_BCD / 2
    body -= radial_slot(lambda x, y: cyl(DOOR_SCREW_D, INNER_T + 2, x, y, z0 - 1),
                        r_door, 0, DOOR_SLOT_PLAY)
    body -= radial_slot(lambda x, y: cyl(INNER_CBORE_D, INNER_CBORE_DEPTH + 1, x, y, z0 - 1),
                        r_door, 0, DOOR_SLOT_PLAY)
    body -= ann_sector(INNER_R_BEAR, INNER_R_OUT + 1, a0 - 20, a1 + 20,
                       INNER_RELIEF + 1, -STEEL_T - INNER_RELIEF)
    return body.rotate([0, 0, 90 * k]) if k else body


# ---------------------------------------------------------------- housing
def window_half_deg():
    """Half angular span of a fan corner window at the skirt's inner radius."""
    y = math.sqrt(SKIRT_R_IN ** 2 - (FAN_W / 2) ** 2)
    return 45.0 - math.degrees(math.atan2(y, FAN_W / 2)) + WINDOW_CLEAR_DEG


def grille_quadrant():
    g = SEAM_GAP / 2
    quad = box(g, 200, g, 200, 0, 100)
    out = None
    for r in GRILLE_RINGS:
        ring = ann_sector(r - GRILLE_BAR / 2, r + GRILLE_BAR / 2, 0, 360, GRILLE_T,
                          Z_PLATE_TOP - GRILLE_T)
        out = ring if out is None else out + ring
    r0 = GRILLE_RINGS[0] - GRILLE_BAR / 2
    for i in range(GRILLE_SPOKES):
        a = 360.0 * i / GRILLE_SPOKES
        if a > 95 and a < 355:
            continue
        out += box(r0, PLATE_OPEN_R + 1.5, -GRILLE_BAR / 2, GRILLE_BAR / 2,
                   Z_PLATE_TOP - GRILLE_T, Z_PLATE_TOP).rotate([0, 0, a])
    return out ^ quad


def housing_quadrant(k=0):
    """Quadrant 0..90 deg: skirt arcs either side of the fan-corner window,
    quarter front plate with grille, M4 counterbore at 45 deg, magnets, tie slots."""
    gp = deg_at(PLATE_OPEN_R, SEAM_GAP / 2)   # at the inner edge, so the gap is >= 0.25 everywhere
    # front plate (plain radial butt seams on the axes)
    plate = ann_sector(PLATE_OPEN_R, PLATE_R, gp, 90 - gp, PLATE_T, Z_FAN_TOP)
    body = plate + grille_quadrant()
    # skirt: two arcs, 0..(45-w) and (45+w)..90, with wall laps at the axes
    w = window_half_deg()
    gi = deg_at(SKIRT_R_IN, SEAM_GAP / 2)
    gm = deg_at(SKIRT_R_IN + WALL / 2, SEAM_GAP / 2)
    go = deg_at(SKIRT_R_OUT, SEAM_GAP / 2)
    r_m = SKIRT_R_IN + WALL / 2
    hz = Z_FAN_TOP - Z_SKIRT_BOTTOM          # exact: tongues must not poke under the neighbour's plate
    # arc at the 0 deg seam: outer half extends to -lap, inner half starts at +lap
    arc0_out = ann_sector(r_m + SEAM_GAP / 2, SKIRT_R_OUT, -WALL_LAP_DEG + go, 45 - w, hz, Z_SKIRT_BOTTOM)
    arc0_in = ann_sector(SKIRT_R_IN, r_m + 1.0, WALL_LAP_DEG + gm, 45 - w, hz, Z_SKIRT_BOTTOM)
    arc0_in -= ann_sector(r_m - SEAM_GAP / 2, r_m + 2, -1, WALL_LAP_DEG + gm, hz + 2, Z_SKIRT_BOTTOM - 1)
    # arc at the 90 deg seam: inner half extends to 90+lap, outer half stops at 90-lap
    arc1_in = ann_sector(SKIRT_R_IN, r_m - SEAM_GAP / 2, 45 + w, 90 + WALL_LAP_DEG - gi, hz, Z_SKIRT_BOTTOM)
    arc1_out = ann_sector(r_m - 1.0, SKIRT_R_OUT, 45 + w, 90 - WALL_LAP_DEG - gm, hz, Z_SKIRT_BOTTOM)
    arc1_out -= ann_sector(r_m - 2, r_m + SEAM_GAP / 2, 90 - WALL_LAP_DEG - gm, 91, hz + 2, Z_SKIRT_BOTTOM - 1)
    body += arc0_out + arc0_in + arc1_in + arc1_out
    # clearance between the tongue tops and the neighbour's plate underside
    body -= ann_sector(SKIRT_R_IN - 1, SKIRT_R_OUT + 1, -WALL_LAP_DEG - 1, 0, TONGUE_TOP_GAP + 1, Z_FAN_TOP - TONGUE_TOP_GAP)
    body -= ann_sector(SKIRT_R_IN - 1, SKIRT_R_OUT + 1, 90, 90 + WALL_LAP_DEG + 1, TONGUE_TOP_GAP + 1, Z_FAN_TOP - TONGUE_TOP_GAP)
    # M4 fan screw: through the plate, head counterbored in the front face
    body -= cyl(FAN_SCREW_D, PLATE_T + 2, FAN_HOLE_XY, FAN_HOLE_XY, Z_FAN_TOP - 1)
    body -= cyl(FAN_SCREW_HEAD_D, FRONT_CBORE_DEPTH + 1, FAN_HOLE_XY, FAN_HOLE_XY,
                Z_PLATE_TOP - FRONT_CBORE_DEPTH)
    # magnet pockets in the front face
    for a in MAGNET_ANGLES:
        body -= cyl(MAGNET_D, MAGNET_H + 1, MAGNET_R * math.cos(rad(a)),
                    MAGNET_R * math.sin(rad(a)), Z_PLATE_TOP - MAGNET_H)
    # cable-tie slots in the wall beside each window (identical on every quadrant)
    for a in TIE_SLOT_ANGLES:
        da = deg_at(r_m, TIE_SLOT[0]) / 2
        body -= ann_sector(SKIRT_R_IN - 1, SKIRT_R_OUT + 1, a - da, a + da, TIE_SLOT[1],
                           TIE_SLOT_Z - TIE_SLOT[1] / 2)
    return body.rotate([0, 0, 90 * k]) if k else body


# ------------------------------------------------------------------ bezel
def bezel_sector(k=0):
    """Pinwheel arc 11.25..101.25 deg so it bridges the housing seams."""
    z0 = Z_PLATE_TOP + MESH_T
    g = deg_at(BEZEL_OPEN_R, SEAM_GAP / 2)
    body = ann_sector(BEZEL_OPEN_R, BEZEL_R, BEZEL_A0 + g, BEZEL_A0 + 90 - g, BEZEL_T, z0)
    for a in (MAGNET_ANGLES[1], MAGNET_ANGLES[0] + 90):   # 40 and 95 deg
        body -= cyl(MAGNET_D, MAGNET_H + 1, MAGNET_R * math.cos(rad(a)),
                    MAGNET_R * math.sin(rad(a)), z0 - 1)
    return body.rotate([0, 0, 90 * k]) if k else body


# ---------------------------------------------------------------- context
def rounded_square(half, r, h, z0=0.0):
    from manifold3d import JoinType
    cs = CrossSection.square([2 * (half - r), 2 * (half - r)], center=True)
    cs = cs.offset(r, JoinType.Round, circular_segments=48)
    return cs.extrude(h).translate([0, 0, z0])


def context_model():
    """Simplified NF-A20 + door section, for the assembly preview only."""
    fan = rounded_square(FAN_W / 2, FAN_CORNER_R, FAN_T, Z_FLANGE)
    fan -= cyl(2 * FAN_OPEN_R, FAN_T + 2, 0, 0, Z_FLANGE - 1, seg=SEG)
    fan += cyl(70, FAN_T - 4, 0, 0, Z_FLANGE + 2, seg=64)
    for a in range(0, 360, 90):
        fan += box(0, FAN_OPEN_R, -4, 4, Z_FLANGE + 1, Z_FLANGE + 5).rotate([0, 0, a + 20])
    for sx in (-1, 1):
        for sy in (-1, 1):
            fan -= cyl(4.3, FAN_T + 2, sx * FAN_HOLE_XY, sy * FAN_HOLE_XY, Z_FLANGE - 1)
    door = box(-150, 150, -150, 150, -STEEL_T, 0)
    door -= cyl(CUTOUT_D, STEEL_T + 2, 0, 0, -STEEL_T - 1, seg=SEG)
    for a in range(0, 360, 45):
        door -= cyl(5.8, STEEL_T + 2, DOOR_BCD / 2 * math.cos(rad(a)),
                    DOOR_BCD / 2 * math.sin(rad(a)), -STEEL_T - 1)
    acrylic = box(0, 150, -150, 150, 0, ACRYLIC_PROUD) - cyl(2 * ACRYLIC_EDGE_R, 10, 0, 0, -1, seg=SEG)
    for a in CAPNUT_ANGLES:
        acrylic += cyl(7, 4, CAPNUT_R * math.cos(rad(a)), CAPNUT_R * math.sin(rad(a)), ACRYLIC_PROUD)
    return fan + door + acrylic


# ------------------------------------------------------------------ export
def flip_for_print(m, z_top):
    return m.rotate([180, 0, 0]).translate([0, 0, z_top])


def export(m, name, z_top=None, centre=True):
    import trimesh
    if z_top is not None:
        m = flip_for_print(m, z_top)
    tm = to_trimesh(m)
    assert tm.is_watertight, name
    bodies = len(tm.split(only_watertight=False))
    if centre:
        b = tm.bounds
        tm.apply_translation([-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]])
    tm.export(os.path.join(OUT, name + ".stl"))
    b = tm.bounds
    print(f"{name:34s} {tm.volume/1000:6.1f} cm3  bodies {bodies}  footprint "
          f"{b[1][0]-b[0][0]:6.1f} x {b[1][1]-b[0][1]:6.1f} x {b[1][2]-b[0][2]:5.1f} mm")
    return tm


def plan_png(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle, Wedge

    fig, ax = plt.subplots(figsize=(9, 9))
    ax.set_aspect("equal")
    ax.add_patch(Circle((0, 0), CUTOUT_D / 2, fill=False, lw=1.5, color="k"))
    for k in range(8):
        a = rad(45 * k)
        ax.add_patch(Circle((104 * math.cos(a), 104 * math.sin(a)), 2.9, fill=False, color="k"))
    ax.add_patch(Circle((0, 0), ACRYLIC_EDGE_R, fill=False, ls="--", color="gray", lw=1.5))
    for a in CAPNUT_ANGLES:
        ax.add_patch(Circle((CAPNUT_R * math.cos(rad(a)), CAPNUT_R * math.sin(rad(a))), 3.5, color="gray"))
    ax.add_patch(Rectangle((-100, -100), 200, 200, fill=False, ls="--", color="tab:blue"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.add_patch(Circle((77 * sx, 77 * sy), 2.25, fill=False, color="tab:blue", lw=1.5))
    cols = ["tab:orange", "tab:green", "tab:red", "tab:purple"]
    for k in range(4):
        base = -22.5 + 90 * k
        ax.add_patch(Wedge((0, 0), R_OUT, base + LAP_HALF, base + 90 + LAP_HALF,
                           width=R_OUT - R_MID, color=cols[k], alpha=0.3, lw=0))
        ax.add_patch(Wedge((0, 0), R_MID, base - LAP_HALF, base + 90 - LAP_HALF,
                           width=R_MID - R_IN, color=cols[k], alpha=0.3, lw=0))
    ax.add_patch(Circle((0, 0), PLATE_R, fill=False, lw=2, color="tab:brown"))
    w = window_half_deg()
    for k in range(4):
        ax.add_patch(Wedge((0, 0), SKIRT_R_OUT, 45 + 90 * k - w, 45 + 90 * k + w,
                           width=WALL, color="tab:red", alpha=0.5, lw=0))
    for k in range(4):
        for a in MAGNET_ANGLES:
            aa = rad(a + 90 * k)
            ax.add_patch(Circle((MAGNET_R * math.cos(aa), MAGNET_R * math.sin(aa)), 3, color="tab:cyan"))
    ax.set_xlim(-150, 150)
    ax.set_ylim(-150, 150)
    ax.set_xlabel("mm   (viewed from OUTSIDE the case)")
    ax.set_title("v3 round housing plan: black = cutout/ring holes, grey = acrylic edge & cap nuts,\n"
                 "colours = plinth sectors (r 90.7-114), brown = plate/bezel r 117,\n"
                 "red = fan-corner windows in the skirt, cyan = magnet pairs, blue = NF-A20")
    ax.grid(True, lw=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=130)


def main():
    os.makedirs(OUT, exist_ok=True)
    for stale in ("housing_corner_x3.stl", "housing_corner_cable_x1.stl"):
        p = os.path.join(OUT, stale)
        if os.path.exists(p):
            os.remove(p)
    fs = flange_sector(0)
    export(fs.rotate([0, 0, -22.5]), "flange_sector_x4", z_top=Z_FLANGE)
    export(inner_ring_sector(0), "inner_ring_sector_x4", z_top=-STEEL_T)
    export(housing_quadrant(0).rotate([0, 0, -45]), "housing_quadrant_x4", z_top=Z_PLATE_TOP)
    export(bezel_sector(0).rotate([0, 0, -(BEZEL_A0 + 45)]), "bezel_sector_x4",
           z_top=Z_PLATE_TOP + MESH_T + BEZEL_T)

    asm = fs
    for k in range(1, 4):
        asm += flange_sector(k)
    for k in range(4):
        asm += inner_ring_sector(k) + housing_quadrant(k) + bezel_sector(k)
    export(asm, "assembly_printed_parts_preview", centre=False)
    export(asm + context_model(), "assembly_with_fan_and_door_preview", centre=False)
    plan_png(os.path.join(os.path.dirname(OUT), "plan_v2.png"))


if __name__ == "__main__":
    sys.exit(main())
