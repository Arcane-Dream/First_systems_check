#!/usr/bin/env python3
"""
NF-A20 external door housing (v2): flange ring + skirt/grille housing +
magnetic mesh bezel, all split to print on a Bambu A1 mini (180 x 180 bed).

Frame of reference (all parts are modelled here, then flipped for printing):
  origin  = centre of the door's round cutout
  x right, y up, AS SEEN FROM OUTSIDE THE CASE
  z       = 0 at the steel's outer face, +z away from the case

Stack (z, mm):     0 .. 14  flange plinth, 210 mm rounded square (bears on steel r 94.5..112.5,
                            underside relieved 4.5 mm beyond r 112.5 and 12 mm beyond r 118)
                  14 .. 44  NF-A20 (exhaust face on the flange, intake out)
                  44 .. 49  housing front plate with spoke grille
                  49 .. 49.3 mesh
                  49.3 .. 52.8 magnetic bezel
                14.5 .. 44  skirt wall (hangs from the plate, sits on the plinth)

Parts (print counts):
  flange_sector        x4   pinwheel quarters of the 210 mm base plinth / mounting ring
  housing_corner       x3   symmetric corner L (front plate + grille + skirt)
  housing_corner_cable x1   same, with the cable window + tie slots; goes bottom-left
  bezel_sector         x4   pinwheel L, clamps the mesh, held by 8 magnet pairs

Run:  python3 build_housing.py     -> stl_v2/*.stl, plan_v2.png
"""
import math
import os
import sys

import numpy as np
from manifold3d import CrossSection, JoinType, Manifold

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
FAN_HOLE_XY = FAN_PITCH / 2            # 77, 77
FAN_OPEN_R = 95.0
FAN_CORNER_R = 8.0

# --------------------------------------------------------------- flange ring
Z_FLANGE = 14.0           # thickness; fan back face sits here
R_IN = 94.5
R_OUT = 160.0             # band cutter radius; real outline is the 210 mm rounded square
R_MID = 105.5
LAP_HALF = 5.0            # deg
SEAM_GAP = 0.25
R_BEAR = 112.5            # door-face contact ends here; relieved beyond
RELIEF_DEPTH = 4.5        # clears the 3.3 mm acrylic step (edge at r 114.7)
R_DEEP_RELIEF = 118.0     # beyond this the underside is cut back to a 2 mm skin
DEEP_RELIEF_DEPTH = 12.0  # clears the acrylic cap nuts (r 125) under the corners
DOOR_SCREW_D = 5.5        # M5 clearance, from INSIDE the case
DOOR_SLOT_PLAY = 1.0
NUT_AF = 8.0 + 0.3        # M5 nut pocket, on the fan face
NUT_POCKET_DEPTH = 6.0        # M5 x 14 tip stays inside the plinth; x16 uses the skirt notch
FAN_SCREW_D = 4.5
FAN_SCREW_HEAD_D = 8.6
FLANGE_FAN_CBORE_DEPTH = Z_FLANGE - 3.5   # 3.5 mm floor -> 6.5 mm thread in fan

# ------------------------------------------------------------------ housing
WALL = 3.0
CLEAR = 2.0
HOUSE_HALF = FAN_W / 2 + CLEAR + WALL      # 105 -> 210 square outside
HOUSE_CORNER_R = 8.0
Z_SKIRT_BOTTOM = Z_FLANGE + 0.5   # skirt sits on the flange plinth, 0.5 mm reveal
Z_FAN_TOP = Z_FLANGE + FAN_T               # 44
PLATE_T = 5.0
Z_PLATE_TOP = Z_FAN_TOP + PLATE_T          # 49
PLATE_OPEN_R = 95.0
FRONT_CBORE_DEPTH = 2.5
GRILLE_T = 3.0
GRILLE_RINGS = (28.0, 50.0, 72.0)
GRILLE_BAR = 3.0
GRILLE_SPOKES = 16                          # every 22.5 deg, includes the axes
WALL_LAP = 6.0
TIP_NOTCH = (7.0, 3.0)                      # half-length along wall, height: clears M5 tips at the seams
# cable window (bottom-left piece): corner window in the skirt + two tie slots
CABLE_WIN = 28.0
CABLE_WIN_TOP = 36.0
TIE_SLOT = (4.0, 3.0)                       # along wall, along z
TIE_SLOT_Y = (66.0, 58.0)
TIE_SLOT_Z = 22.0

# -------------------------------------------------------------------- bezel
MESH_T = 0.3
BEZEL_T = 3.5
BEZEL_OPEN_R = 92.0
MAGNET_D = 6.0 + 0.4
MAGNET_H = 2.0 + 0.2
MAGNET_R = 100.0
MAGNET_ANGLES = (5.0, 40.0)                 # per quadrant, +90k -> 8 magnets
BEZEL_A0 = 11.25                            # bezel pinwheel seam; bezel spans 11.25..101.25

SEG = 256
HOLE_SEG = 48
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl_v2")


# ------------------------------------------------------------------ helpers
def rad(a):
    return math.radians(a)


def ann_sector(r1, r2, a0, a1, h, z0=0.0):
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


def rounded_square(half, r, h, z0=0.0):
    cs = CrossSection.square([2 * (half - r), 2 * (half - r)], center=True)
    cs = cs.offset(r, JoinType.Round, circular_segments=48)
    return cs.extrude(h).translate([0, 0, z0])


def to_trimesh(m):
    import trimesh
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    f = np.asarray(mesh.tri_verts)
    return trimesh.Trimesh(v, f, process=False)


# ------------------------------------------------------------- flange ring
def flange_sector(k=0):
    """Pinwheel sector: door screw at 0 deg, fan screw at 45 deg."""
    a0, a1 = -22.5, 67.5
    g_out = math.degrees(SEAM_GAP / 2 / R_OUT)
    g_in = math.degrees(SEAM_GAP / 2 / R_IN)
    body = (ann_sector(R_MID + SEAM_GAP / 2, R_OUT,
                       a0 + LAP_HALF + g_out, a1 + LAP_HALF - g_out, Z_FLANGE)
            + ann_sector(R_IN, R_MID - SEAM_GAP / 2,
                         a0 - LAP_HALF + g_in, a1 - LAP_HALF - g_in, Z_FLANGE))
    body = body ^ rounded_square(HOUSE_HALF, HOUSE_CORNER_R, Z_FLANGE + 2, -1)
    r_door = DOOR_BCD / 2
    # M5 from inside: through slot + captive nut pocket on the fan face (z = top)
    body -= radial_slot(lambda x, y: cyl(DOOR_SCREW_D, Z_FLANGE + 2, x, y, -1),
                        r_door, 0, DOOR_SLOT_PLAY)
    body -= radial_slot(lambda x, y: hexp(NUT_AF, NUT_POCKET_DEPTH + 1, x, y,
                                          Z_FLANGE - NUT_POCKET_DEPTH),
                        r_door, 0, DOOR_SLOT_PLAY)
    # fan screw from the door face: through hole + deep counterbore
    body -= cyl(FAN_SCREW_D, Z_FLANGE + 2, FAN_HOLE_XY, FAN_HOLE_XY, -1)
    body -= cyl(FAN_SCREW_HEAD_D, FLANGE_FAN_CBORE_DEPTH + 1, FAN_HOLE_XY, FAN_HOLE_XY, -1)
    # door-face relief beyond the bearing radius (acrylic step)
    body -= ann_sector(R_BEAR, R_OUT + 1, a0 - 20, a1 + 20, RELIEF_DEPTH + 1, -1)
    body -= ann_sector(R_DEEP_RELIEF, R_OUT + 1, a0 - 20, a1 + 20, DEEP_RELIEF_DEPTH + 1, -1)
    return body.rotate([0, 0, 90 * k]) if k else body


# ---------------------------------------------------------------- housing
def grille_full():
    g = None
    for r in GRILLE_RINGS:
        ring = ann_sector(r - GRILLE_BAR / 2, r + GRILLE_BAR / 2, 0, 360, GRILLE_T,
                          Z_PLATE_TOP - GRILLE_T)
        g = ring if g is None else g + ring
    r0 = GRILLE_RINGS[0] - GRILLE_BAR / 2
    for i in range(GRILLE_SPOKES):
        a = 360.0 * i / GRILLE_SPOKES
        sp = box(r0, PLATE_OPEN_R + 1.5, -GRILLE_BAR / 2, GRILLE_BAR / 2,
                 Z_PLATE_TOP - GRILLE_T, Z_PLATE_TOP).rotate([0, 0, a])
        g += sp
    return g


def housing_full():
    outer = rounded_square(HOUSE_HALF, HOUSE_CORNER_R, Z_PLATE_TOP - Z_SKIRT_BOTTOM,
                           Z_SKIRT_BOTTOM)
    inner = rounded_square(HOUSE_HALF - WALL, HOUSE_CORNER_R - WALL,
                           Z_FAN_TOP - Z_SKIRT_BOTTOM + 0.01, Z_SKIRT_BOTTOM - 0.01)
    body = outer - inner
    body -= cyl(2 * PLATE_OPEN_R, PLATE_T + 2, 0, 0, Z_FAN_TOP - 1, seg=SEG)
    body += grille_full()
    return body


def housing_corner(k=0, cable=False):
    """Symmetric corner L in quadrant x>=0, y>=0 (corner at +105,+105)."""
    g = SEAM_GAP / 2
    quad = box(g, HOUSE_HALF + 2, g, HOUSE_HALF + 2, 0, Z_PLATE_TOP + 1)
    body = housing_full() ^ quad
    zb, zt = Z_SKIRT_BOTTOM - 0.01, Z_FAN_TOP
    xi, xm, xo = HOUSE_HALF - WALL, HOUSE_HALF - WALL / 2, HOUSE_HALF
    # right wall (seam at y = 0): inner half cut back, outer half extended
    body -= box(xi - 1, xm + g, -1, WALL_LAP + g, zb, zt)
    body += box(xm + g, xo, -WALL_LAP, g, Z_SKIRT_BOTTOM, zt)
    # top wall (seam at x = 0): outer half cut back, inner half extended
    body -= box(-1, WALL_LAP + g, xm + g, xo + 1, zb, zt)
    body += box(-WALL_LAP, g, xi, xm - g, Z_SKIRT_BOTTOM, zt)
    # notch in the skirt bottom over the door screws (they sit on the seams)
    body -= box(xi - 1, xo + 1, -TIP_NOTCH[0], TIP_NOTCH[0], zb, Z_SKIRT_BOTTOM + TIP_NOTCH[1])
    body -= box(-TIP_NOTCH[0], TIP_NOTCH[0], xi - 1, xo + 1, zb, Z_SKIRT_BOTTOM + TIP_NOTCH[1])
    # fan screw (stock fan screw from the front into the fan corner)
    body -= cyl(FAN_SCREW_D, PLATE_T + 2, FAN_HOLE_XY, FAN_HOLE_XY, Z_FAN_TOP - 1)
    body -= cyl(FAN_SCREW_HEAD_D, FRONT_CBORE_DEPTH + 1, FAN_HOLE_XY, FAN_HOLE_XY,
                Z_PLATE_TOP - FRONT_CBORE_DEPTH)
    # magnet pockets in the front face
    for a in MAGNET_ANGLES:
        body -= cyl(MAGNET_D, MAGNET_H + 1, MAGNET_R * math.cos(rad(a)),
                    MAGNET_R * math.sin(rad(a)), Z_PLATE_TOP - MAGNET_H)
    if cable:
        w0 = HOUSE_HALF - CABLE_WIN
        body -= box(w0, HOUSE_HALF + 1, w0, HOUSE_HALF + 1, Z_SKIRT_BOTTOM - 1, CABLE_WIN_TOP)
        for y in TIE_SLOT_Y:
            body -= box(xi - 1, xo + 1, y - TIE_SLOT[0] / 2, y + TIE_SLOT[0] / 2,
                        TIE_SLOT_Z - TIE_SLOT[1] / 2, TIE_SLOT_Z + TIE_SLOT[1] / 2)
    return body.rotate([0, 0, 90 * k]) if k else body


# ------------------------------------------------------------------ bezel
def bezel_sector(k=0):
    """Pinwheel L spanning 11.25..101.25 deg so it bridges the housing seams."""
    z0 = Z_PLATE_TOP + MESH_T
    a0, a1 = BEZEL_A0, BEZEL_A0 + 90
    plate = rounded_square(HOUSE_HALF, HOUSE_CORNER_R, BEZEL_T, z0)
    plate -= cyl(2 * BEZEL_OPEN_R, BEZEL_T + 2, 0, 0, z0 - 1, seg=SEG)
    # angular wedge with the seam gap
    big = 400.0
    g0 = a0 + math.degrees(SEAM_GAP / 2 / 100)
    g1 = a1 - math.degrees(SEAM_GAP / 2 / 100)
    wedge = CrossSection([[(0, 0), (big * math.cos(rad(g0)), big * math.sin(rad(g0))),
                           (big * math.cos(rad((g0 + g1) / 2)), big * math.sin(rad((g0 + g1) / 2))),
                           (big * math.cos(rad(g1)), big * math.sin(rad(g1)))]]) \
        .extrude(BEZEL_T + 2).translate([0, 0, z0 - 1])
    body = plate ^ wedge
    for a in (MAGNET_ANGLES[1], MAGNET_ANGLES[0] + 90):   # 40 and 95 deg: bridges the housing seam
        body -= cyl(MAGNET_D, MAGNET_H + 1, MAGNET_R * math.cos(rad(a)),
                    MAGNET_R * math.sin(rad(a)), z0 - 1)
    return body.rotate([0, 0, 90 * k]) if k else body


# ---------------------------------------------------------------- context
def context_model():
    """Simplified NF-A20 + door section, for the assembly preview only."""
    fan = rounded_square(FAN_W / 2, FAN_CORNER_R, FAN_T, Z_FLANGE)
    fan -= cyl(2 * FAN_OPEN_R, FAN_T + 2, 0, 0, Z_FLANGE - 1, seg=SEG)
    fan += cyl(70, FAN_T - 4, 0, 0, Z_FLANGE + 2, seg=64)          # hub
    for a in range(0, 360, 90):
        fan += box(0, FAN_OPEN_R, -4, 4, Z_FLANGE + 1, Z_FLANGE + 5).rotate([0, 0, a + 20])
    for sx in (-1, 1):
        for sy in (-1, 1):
            fan -= cyl(4.3, FAN_T + 2, sx * FAN_HOLE_XY, sy * FAN_HOLE_XY, Z_FLANGE - 1)
    door = box(-140, 140, -140, 140, -STEEL_T, 0)
    door -= cyl(CUTOUT_D, STEEL_T + 2, 0, 0, -STEEL_T - 1, seg=SEG)
    for a in range(0, 360, 45):
        door -= cyl(5.8, STEEL_T + 2, DOOR_BCD / 2 * math.cos(rad(a)),
                    DOOR_BCD / 2 * math.sin(rad(a)), -STEEL_T - 1)
    acrylic = box(0, 140, -140, 140, 0, ACRYLIC_PROUD) - cyl(2 * ACRYLIC_EDGE_R, 10, 0, 0, -1, seg=SEG)
    for a in CAPNUT_ANGLES:
        acrylic += cyl(7, 4, CAPNUT_R * math.cos(rad(a)), CAPNUT_R * math.sin(rad(a)), ACRYLIC_PROUD)
    return fan + door + acrylic


# ------------------------------------------------------------------ export
def flip_for_print(m, z_top):
    """Rotate so the face at z_top lies on the bed at z = 0."""
    return m.rotate([180, 0, 0]).translate([0, 0, z_top])


def export(m, name, z_top=None, centre=True):
    if z_top is not None:
        m = flip_for_print(m, z_top)
    tm = to_trimesh(m)
    assert tm.is_watertight, name
    if centre:
        b = tm.bounds
        tm.apply_translation([-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]])
    tm.export(os.path.join(OUT, name + ".stl"))
    b = tm.bounds
    print(f"{name:34s} {tm.volume/1000:6.1f} cm3  footprint "
          f"{b[1][0]-b[0][0]:6.1f} x {b[1][1]-b[0][1]:6.1f} x {b[1][2]-b[0][2]:5.1f} mm")
    return tm


def plan_png(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Wedge

    fig, ax = plt.subplots(figsize=(9, 9))
    ax.set_aspect("equal")
    ax.add_patch(Circle((0, 0), CUTOUT_D / 2, fill=False, lw=1.5, color="k"))
    for k in range(8):
        a = rad(45 * k)
        ax.add_patch(Circle((104 * math.cos(a), 104 * math.sin(a)), 2.9, fill=False, color="k"))
    ax.add_patch(Circle((0, 0), ACRYLIC_EDGE_R, fill=False, ls="--", color="gray"))
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
    ax.add_patch(FancyBboxPatch((-105 + 8, -105 + 8), 210 - 16, 210 - 16,
                                boxstyle="round,pad=8", fill=False, lw=2, color="tab:brown"))
    ax.plot([0, 0], [95, 105], "k-", lw=0.8)
    ax.plot([0, 0], [-95, -105], "k-", lw=0.8)
    ax.plot([95, 105], [0, 0], "k-", lw=0.8)
    ax.plot([-95, -105], [0, 0], "k-", lw=0.8)
    ax.add_patch(Rectangle((-105, -105), CABLE_WIN, CABLE_WIN, color="tab:red", alpha=0.5))
    for k in range(4):
        for a in MAGNET_ANGLES:
            aa = rad(a + 90 * k)
            ax.add_patch(Circle((MAGNET_R * math.cos(aa), MAGNET_R * math.sin(aa)), 3, color="tab:cyan"))
    ax.set_xlim(-150, 150)
    ax.set_ylim(-150, 150)
    ax.set_xlabel("mm   (viewed from OUTSIDE the case)")
    ax.set_title("v2 housing plan: black = door cutout/ring holes, grey = acrylic edge & cap nuts,\n"
                 "colours = flange sectors, brown = 210 mm housing outline (seams on the axes),\n"
                 "cyan = magnet pairs, red = cable window (bottom-left)")
    ax.grid(True, lw=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=130)


def main():
    os.makedirs(OUT, exist_ok=True)
    fs = flange_sector(0)
    export(fs.rotate([0, 0, -22.5]), "flange_sector_x4", z_top=Z_FLANGE)
    hc = housing_corner(0)
    export(hc, "housing_corner_x3", z_top=Z_PLATE_TOP)
    hcc = housing_corner(0, cable=True)
    export(hcc, "housing_corner_cable_x1", z_top=Z_PLATE_TOP)
    bz = bezel_sector(0)
    export(bz.rotate([0, 0, -(BEZEL_A0 + 45)]), "bezel_sector_x4", z_top=Z_PLATE_TOP + MESH_T + BEZEL_T)

    asm = fs
    for k in range(1, 4):
        asm += flange_sector(k)
    for k in range(4):
        asm += housing_corner(k, cable=(k == 2))      # k=2 -> bottom-left corner
        asm += bezel_sector(k)
    export(asm, "assembly_printed_parts_preview", centre=False)
    export(asm + context_model(), "assembly_with_fan_and_door_preview", centre=False)
    plan_png(os.path.join(os.path.dirname(OUT), "plan_v2.png"))


if __name__ == "__main__":
    sys.exit(main())
