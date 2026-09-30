#!/usr/bin/env python3
"""
NF-A20 -> case-door adapter ring.  Generates the STLs with manifold3d.

The door has a ~187 mm round cutout with 8 x 5.8 mm holes on a 208 mm bolt
circle (holes at 0/45/90/... deg).  The Noctua NF-A20 has 4 holes on a
154 mm square, i.e. r = 108.9 mm at 45/135/225/315 deg -- only 5 mm outside
the door's diagonal holes, so those can't both be used.  This adapter:

  * bolts to the door through the 4 ORTHOGONAL ring holes (M5 + nut),
  * carries the fan on the 4 DIAGONAL positions (stock fan screws),
  * is a full 360 deg shroud so the fan pulls air only through the cutout,
  * is split into 4 identical 90 deg sectors so it prints on an A1 mini
    (180 x 180 bed).  Sectors mate with a staggered radial lap so the seam
    is not a straight air gap and the pieces self-locate.

Coordinates: origin = centre of the round cutout, +Z points INTO the case.
Sector 0 is exported with its FAN face on Z=0 (print it that way up).

Run:  python3 build_adapter.py            -> writes stl/*.stl + plan.png
"""
import math
import os
import sys

import numpy as np
from manifold3d import CrossSection, Manifold

# ----------------------------------------------------------------- inputs --
# Door (from caliper / tape measurements, converted and rounded to metric)
DOOR_BCD = 208.0          # 8-hole bolt circle, mm  (measured 207.7)
DOOR_HOLE_D = 5.8         # mm (measured 5.70-5.82)
CUTOUT_D = 187.0          # mm (tape measurement)
STEEL_T = 0.86            # mm (0.034")

# Fan: Noctua NF-A20 (200 x 200 x 30, 154 mm hole square)
FAN_HOLE_PITCH = 154.0
FAN_HOLE_R = FAN_HOLE_PITCH / math.sqrt(2)   # 108.89 mm

# Adapter
T = 8.0                   # plate thickness
R_IN = 94.5               # inner radius: 1 mm outside the cutout edge
R_OUT = 117.0             # outer radius
R_MID = 105.5             # radius of the lap step between inner/outer bands
LAP_HALF = 5.0            # deg: each band overhangs the nominal seam by this
SEAM_GAP = 0.25           # mm clearance at every mating face

# Door screw: M5 from OUTSIDE, into a hex nut captured on the fan face
DOOR_SCREW_D = 5.5        # clearance for M5
DOOR_SLOT_PLAY = 1.0      # +/- radial play (covers BCD uncertainty)
NUT_AF = 8.0              # M5 hex nut across flats
NUT_AF_CLEAR = 0.3
NUT_H = 4.7               # ISO 4032 M5 (DIN 934 is 4.0)
NUT_POCKET_DEPTH = NUT_H + 0.2

# Fan screw: stock self-tapping fan screw (5/32" x 10 mm) inserted from the
# DOOR face of the adapter, threads into the fan's corner.
FAN_SCREW_HOLE_D = 4.5
FAN_SCREW_CBORE_D = 9.0
FAN_SCREW_CBORE_DEPTH = 4.5   # leaves 3.5 mm plate -> 6.5 mm of thread in fan

# Relief on the door face around the outer rim so the adapter never sits on
# the (near-flush) heads of the acrylic window screws at r ~ 119-128 mm.
RELIEF_R = 113.0
RELIEF_DEPTH = 1.5

SEG = 256                 # polygon resolution for big arcs
HOLE_SEG = 48

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")


# --------------------------------------------------------------- helpers --
def annular_sector(r1, r2, a0, a1, h, z0=0.0):
    """Extruded annulus sector between angles a0..a1 (deg, CCW)."""
    n = max(4, int(SEG * (a1 - a0) / 360.0))
    outer = [(r2 * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
              r2 * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
             for i in range(n + 1)]
    inner = [(r1 * math.cos(math.radians(a1 - (a1 - a0) * i / n)),
              r1 * math.sin(math.radians(a1 - (a1 - a0) * i / n)))
             for i in range(n + 1)]
    cs = CrossSection([outer + inner])
    return cs.extrude(h).translate([0, 0, z0])


def cyl(d, h, x=0.0, y=0.0, z=0.0, seg=HOLE_SEG):
    return Manifold.cylinder(h, d / 2, d / 2, seg).translate([x, y, z])


def hex_prism(af, h, x=0.0, y=0.0, z=0.0):
    # circumradius of a hexagon from across-flats
    r = af / math.sqrt(3)
    return Manifold.cylinder(h, r, r, 6).translate([x, y, z])


def radial_slot_cyl(d, h, r_c, ang_deg, play, z=0.0):
    """Cylinder slot elongated radially by +/- play, centred at (r_c, ang)."""
    a = math.radians(ang_deg)
    c1 = cyl(d, h, (r_c - play) * math.cos(a), (r_c - play) * math.sin(a), z)
    c2 = cyl(d, h, (r_c + play) * math.cos(a), (r_c + play) * math.sin(a), z)
    return Manifold.hull(c1 + c2) if hasattr(Manifold, "hull") else (c1 + c2).hull()


def radial_slot_hex(af, h, r_c, ang_deg, play, z=0.0):
    a = math.radians(ang_deg)
    h1 = hex_prism(af, h, (r_c - play) * math.cos(a), (r_c - play) * math.sin(a), z)
    h2 = hex_prism(af, h, (r_c + play) * math.cos(a), (r_c + play) * math.sin(a), z)
    return (h1 + h2).hull()


def sector(index=0):
    """One 90 deg sector.  index rotates it into place (0..3)."""
    # nominal span of sector 0: -22.5 .. 67.5 deg (door hole at 0, fan at 45)
    a0, a1 = -22.5, 67.5
    # angular clearance so mating faces don't touch: gap/2 on each side
    g_out = math.degrees(SEAM_GAP / 2 / R_OUT)
    g_in = math.degrees(SEAM_GAP / 2 / R_IN)
    outer = annular_sector(R_MID + SEAM_GAP / 2, R_OUT,
                           a0 + LAP_HALF + g_out, a1 + LAP_HALF - g_out, T)
    inner = annular_sector(R_IN, R_MID - SEAM_GAP / 2,
                           a0 - LAP_HALF + g_in, a1 - LAP_HALF - g_in, T)
    body = outer + inner

    # --- door attachment at 0 deg, r = BCD/2 -----------------------------
    r_door = DOOR_BCD / 2
    body -= radial_slot_cyl(DOOR_SCREW_D, T + 2, r_door, 0, DOOR_SLOT_PLAY, -1)
    body -= radial_slot_hex(NUT_AF + NUT_AF_CLEAR, NUT_POCKET_DEPTH + 1,
                            r_door, 0, DOOR_SLOT_PLAY, -1)  # pocket on fan face (z=0)

    # --- fan attachment at 45 deg, r = 108.9 ------------------------------
    fx = fy = FAN_HOLE_PITCH / 2
    body -= cyl(FAN_SCREW_HOLE_D, T + 2, fx, fy, -1)
    body -= cyl(FAN_SCREW_CBORE_D, FAN_SCREW_CBORE_DEPTH + 1, fx, fy,
                T - FAN_SCREW_CBORE_DEPTH)                 # counterbore on door face

    # --- rim relief on the door face --------------------------------------
    relief = annular_sector(RELIEF_R, R_OUT + 1, a0 - 20, a1 + 20,
                            RELIEF_DEPTH + 1, T - RELIEF_DEPTH)
    body -= relief

    if index:
        body = body.rotate([0, 0, 90 * index])
    return body


def to_trimesh(m):
    import trimesh
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    f = np.asarray(mesh.tri_verts)
    return trimesh.Trimesh(v, f, process=False)


def plan_png(path):
    """2-D plan view of the assembled adapter over the door hole pattern."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle, Wedge

    fig, ax = plt.subplots(figsize=(9, 9))
    ax.set_aspect("equal")
    # door cutout + ring holes
    ax.add_patch(Circle((0, 0), CUTOUT_D / 2, fill=False, lw=1.5, color="k"))
    for k in range(8):
        a = math.radians(45 * k)
        r = DOOR_BCD / 2
        ax.add_patch(Circle((r * math.cos(a), r * math.sin(a)), DOOR_HOLE_D / 2,
                            fill=False, color="k", lw=1.2))
    # fan outline & holes
    ax.add_patch(Rectangle((-100, -100), 200, 200, fill=False, ls="--", color="tab:blue"))
    ax.add_patch(Circle((0, 0), 95, fill=False, ls=":", color="tab:blue"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.add_patch(Circle((77 * sx, 77 * sy), 2.25, color="tab:blue", fill=False, lw=1.5))
    # sectors
    cols = ["tab:orange", "tab:green", "tab:red", "tab:purple"]
    for k in range(4):
        base = -22.5 + 90 * k
        ax.add_patch(Wedge((0, 0), R_OUT, base + LAP_HALF, base + 90 + LAP_HALF,
                           width=R_OUT - R_MID, color=cols[k], alpha=0.35, lw=0))
        ax.add_patch(Wedge((0, 0), R_MID, base - LAP_HALF, base + 90 - LAP_HALF,
                           width=R_MID - R_IN, color=cols[k], alpha=0.35, lw=0))
        a = math.radians(90 * k)
        ax.add_patch(Circle((DOOR_BCD / 2 * math.cos(a), DOOR_BCD / 2 * math.sin(a)),
                            NUT_AF / math.sqrt(3), fill=False, color="k", ls="-", lw=0.8))
    ax.add_patch(Circle((0, 0), RELIEF_R, fill=False, ls=":", color="gray", lw=0.8))
    ax.set_xlim(-150, 150)
    ax.set_ylim(-150, 150)
    ax.set_xlabel("mm")
    ax.set_title("NF-A20 door adapter, viewed from inside the case\n"
                 "black = door cutout / 8 ring holes, blue = NF-A20 frame & holes,\n"
                 "colours = the 4 identical printed sectors (staggered lap seams)")
    ax.grid(True, lw=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=130)


def main():
    os.makedirs(OUT, exist_ok=True)
    s0 = sector(0)
    tm = to_trimesh(s0)
    assert tm.is_watertight, "sector mesh not watertight"
    bb = tm.bounds
    print(f"sector: volume {tm.volume/1000:.1f} cm^3, bbox "
          f"{bb[1][0]-bb[0][0]:.1f} x {bb[1][1]-bb[0][1]:.1f} x {bb[1][2]-bb[0][2]:.1f} mm")

    # Export sector 0 rotated so its long axis is along X and centred at origin.
    # Nominal centre angle is 22.5 deg -> rotate by -22.5.
    s_print = s0.rotate([0, 0, -22.5])
    tp = to_trimesh(s_print)
    tp.apply_translation(-np.array([(tp.bounds[0][0] + tp.bounds[1][0]) / 2,
                                    (tp.bounds[0][1] + tp.bounds[1][1]) / 2, 0]))
    b = tp.bounds
    print(f"print footprint: {b[1][0]-b[0][0]:.1f} x {b[1][1]-b[0][1]:.1f} mm "
          f"(rotate 45 deg on the A1 mini plate if the slicer complains)")
    tp.export(os.path.join(OUT, "nfa20_door_adapter_sector_x4.stl"))

    asm = s0
    for k in range(1, 4):
        asm += sector(k)
    ta = to_trimesh(asm)
    ta.export(os.path.join(OUT, "nfa20_door_adapter_assembled_preview.stl"))
    print("assembled preview:", ta.bounds.round(1).tolist())

    plan_png(os.path.join(os.path.dirname(OUT), "plan.png"))
    print("wrote", OUT)


if __name__ == "__main__":
    sys.exit(main())
