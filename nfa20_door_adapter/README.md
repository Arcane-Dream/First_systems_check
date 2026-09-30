# NF-A20 side-door fan housing

Two designs live here.

* **v2 (current): external housing.** The NF-A20 mounts on the *outside* of the
  door in a 210 mm square housing with a base plinth, skirt, spoke grille,
  magnetic mesh dust filter, and a cable window at the bottom-left corner for
  the fan lead to run round to the rear grommet. Files: `stl_v2/`,
  `build_housing.py`, `nfa20_door_housing.scad`, `plan_v2.png`,
  `preview/renders_v2.png`.
* **v1: inside-mount ring.** The original bare adapter ring for mounting the
  fan on the inside face of the door. Kept for reference at the bottom of this
  file. Files: `stl/`, `build_adapter.py`, `nfa20_door_adapter.scad`, `plan.png`.

Both builders produce identical solids from the OpenSCAD and Python sources.

---

## v2: external housing

### What the photos add to the measurements

Fitting a perspective transform to the eight ring holes (all within 1 mm)
puts the acrylic window's fasteners on a **125 mm radius** at 96, 44, 0, -45
and -96 degrees (outside view), and the acrylic's inner edge at **r 114.7 mm**.
The two nuts at +/-45 degrees sit directly under the fan's corners, so the fan
has to stand off the steel; the acrylic step means the base can only bear on
bare steel inside r 112.5.

### Stack, from the steel outward

| z (mm) | Part | Notes |
|---|---|---|
| 0 to 14 | flange plinth (4 pinwheel pieces) | 210 mm rounded square. Bears on steel r 94.5 to 112.5 only. Underside relieved 4.5 mm beyond r 112.5 (acrylic step) and 12 mm beyond r 118 (cap nuts). |
| 14 to 44 | NF-A20 | exhaust face on the plinth, intake outward. Screwed to the plinth from underneath with 4 stock fan screws (counterbored, hidden against the steel). |
| 14.5 to 44 | skirt (4 corner pieces) | 3 mm walls, 2 mm clearance to the fan, sits on the plinth with a 0.5 mm reveal. Corner pieces lap-joint at the wall seams. |
| 44 to 49 | front plate + spoke grille | 5 mm plate, 16 spokes and 3 rings, 3 mm thick. Attached to the fan's front with 4 more stock fan screws (counterbored). |
| 49 to 49.3 | mesh | your filter mesh, cut ~205 x 205 mm |
| 49.3 to 52.8 | bezel (4 pinwheel pieces) | 3.5 mm, r 92 opening, held by 8 pairs of 6 x 2 mm magnets. Pull it off to clean the mesh. |

Total stand-off from the door: about 53 mm.

### Why it's shaped this way

* **Door bolts on the axes, fan screws on the diagonals** (same reason as v1:
  the fan holes at r 108.9 sit only 5 mm from the door's diagonal holes).
  The M5 bolts go in from *inside* the case into nuts captured in the plinth,
  so nothing shows on the outside and the fan can go on before the plinth
  goes on the door.
* **The plinth is a full 210 mm square, not a ring**, because a 117 mm ring
  would have run under the skirt walls. Making it the housing's base also
  closes the gap under the skirt.
* **Housing seams are on the axes** (each corner piece is a symmetric L) and
  **bezel seams are 11.25 degrees off the axes**, with the magnets at 5 and 40
  degrees in each quadrant, so every bezel piece is held by one magnet on each
  of two housing pieces and ties the housing seams together.
* **Grille seams run down the middle of the 0/90/180/270 spokes**, so the
  split shows as a hairline in a spoke rather than a broken ring.
* **Door screws sit on the housing seams**, so the skirt has a 14 x 3 mm notch
  at each wall end; an M5 x 16 tip clears it, M5 x 14 stays inside the plinth.
* **Cable window**: the bottom-left corner piece has a 28 x 28 mm window in
  the skirt from the plinth up to z 36, plus two 4 x 3 mm slots on the bottom
  wall for a cable tie. Rotate the fan so its lead leaves at that corner; the
  lead exits the window, drops down the 14 mm plinth wall to the door, and
  runs off to the rear grommet.

### Hardware

| Qty | Item | Where |
|---|---|---|
| 4 | M5 x 14 or x 16 screw (any head) + washer | from inside the case, through the door's top/bottom/left/right ring holes |
| 4 | M5 plain hex nut | plinth pockets (fan face); ISO 4032 (4.7 mm) or DIN 934 (4.0 mm) both fit, nyloc doesn't |
| 8 | standard self-tapping fan screws | 4 plinth-to-fan (from underneath), 4 plate-to-fan (from the front). The Noctua box has 4. |
| 16 | 6 x 2 mm neodymium disc magnets | 8 in the plate, 8 in the bezel. Mind polarity: set all plate magnets the same way up, then let each bezel magnet snap onto its partner before gluing. Press-fit; a drop of CA to be sure. |
| 1 | mesh, ~205 x 205 mm | cut from a cheap 200 mm PC dust filter or fine nylon mesh |
| 1 | cable tie | optional strain relief at the window |

### Printing (A1 mini)

All parts are exported with their print face on Z = 0. No supports.

| File | Print | Footprint | Orientation |
|---|---|---|---|
| `flange_sector_x4.stl` | 4 | 165 x 74 x 14 | fan face down (nut pocket becomes a short bridge) |
| `housing_corner_x3.stl` | 3 | 111 x 111 x 34.5 | front face down, walls up |
| `housing_corner_cable_x1.stl` | 1 | 111 x 111 x 34.5 | same |
| `bezel_sector_x4.stl` | 4 | 151 x 77 x 3.5 | front face down |

PETG or PLA, 0.2 mm layers, 4 walls, 30 % infill. Two corner pieces fit one
plate; the flange and bezel go one or two per plate (rotate 45 degrees if the
slicer complains). The seams have 0.25 mm total clearance; if your printer
runs fat, scale nothing, just sand the lap tongues.

### Assembly

1. Press magnets into the 8 plate pockets and 8 bezel pockets (see polarity note).
2. Drop an M5 nut into each plinth piece's hex pocket.
3. Lay the four plinth pieces on the fan's **exhaust** face, laps interlocked,
   and drive a fan screw through each deep counterbore into the fan corner.
4. Set the four corner pieces over the fan's **intake** face (laps interlocked,
   the cable-window piece at the fan's cable corner) and drive a fan screw
   through each front counterbore into the fan.
5. Feed the fan lead out through the window; tie it off through the slots.
6. Offer the whole unit up to the outside of the door with the cable window
   bottom-left, and fit the four M5 screws from inside the case.
7. Lay the mesh on the front plate and snap the four bezel pieces on.

### Checks before printing all of it

* Print one `flange_sector` first and offer it up to the door: the slot should
  land on a ring hole, the bearing band should sit flat, and the outer skin
  must clear the acrylic's cap nuts. If a nut is taller than ~8 mm above the
  acrylic, raise `DEEP_RELIEF_DEPTH` (or `Z_FLANGE`).
* Print one `housing_corner` and one `bezel_sector` and check the magnet fit.

---

## v1: inside-mount adapter ring (original design)

Adapter ring that mounts a Noctua NF-A20 (200 x 200 x 30 mm, 154 mm hole
square) on the inside of the case door, over the door's ~187 mm round cutout,
using the door's existing 8-hole bolt ring. Designed for a Bambu Lab A1 mini
(180 x 180 mm bed), so it prints as four identical 90-degree sectors.

Files:

| File | What |
|---|---|
| `stl/nfa20_door_adapter_sector_x4.stl` | The printable part. **Print 4.** |
| `stl/nfa20_door_adapter_assembled_preview.stl` | All four sectors assembled, for checking fit in CAD. Not for printing. |
| `nfa20_door_adapter.scad` | Parametric OpenSCAD source (all dimensions at the top). |
| `build_adapter.py` | Python/manifold3d build that produced the STLs, plus `plan.png`. Both sources render to the identical solid. |
| `plan.png` | Plan view of the assembled ring over the door hole pattern and the fan outline. |

## Dimensions worked out from the measurements

| Measured | Value | Metric | Used as |
|---|---|---|---|
| Ring hole, inner-to-inner (adjacent holes) | 2.905" | 73.79 mm | |
| Ring hole, outer-to-outer (adjacent holes) | 3.354" | 85.19 mm | |
| Centre-to-centre, adjacent holes (average of the two) | 3.1295" | 79.49 mm | |
| Hole diameter (direct) | 0.229" | 5.82 mm | 5.8 mm |
| Hole diameter (from outer minus inner, halved) | 0.2245" | 5.70 mm | agrees, so the spacing number is trustworthy |
| Bolt circle for 8 equally spaced holes: 79.49 / sin(22.5 deg) | | 207.7 mm | **208 mm** (r = 104) |
| Round cutout (tape) | | ~187 mm | r = 93.5 |
| Steel gauge | 0.034" | 0.86 mm | 0.8 to 0.9 mm sheet |
| Acrylic proud of the steel (outside) | 0.13" | 3.3 mm | 3 mm sheet plus paint/gap |

The photos show the 8 ring holes sit at 0, 45, 90 ... degrees, i.e. four on the
vertical/horizontal axes and four on the diagonals.

The NF-A20's holes are on a 154 mm square, which is r = 108.9 mm at 45, 135,
225 and 315 degrees. The door's four *diagonal* ring holes are at r = 104 mm at
the same angles, so the two patterns miss each other by only 5 mm and cannot
both be used as holes in the same part. The adapter therefore:

* bolts to the door through the four **orthogonal** ring holes (top, bottom,
  left, right), M5 screws from outside into captured nuts;
* carries the fan on the four **diagonal** positions with the stock fan screws;
* leaves the door's four diagonal holes unused (they end up under the fan-screw
  counterbores; harmless).

The acrylic window's screws show up on the inside face as nearly flush flat
heads at roughly r = 119 to 128 mm. The ring's outer radius is 117 mm and its
door face has a 1.5 mm relief from r = 113 mm outward, so it never bears on
those heads.

## Adapter geometry

* Full 360-degree shroud, 8 mm thick, inner r 94.5 mm (1 mm outside the cutout
  edge), outer r 117 mm. The fan frame's flat (r 95 to 100 at the middle of each
  side) lands on the ring, so intake air comes through the cutout rather than
  around the fan's edge.
* Four identical sectors. Each spans 90 degrees nominally (-22.5 to +67.5),
  with the door hole at 0 degrees and the fan hole at 45 degrees. The outer band
  (r 105.5 to 117) is shifted +5 degrees and the inner band (r 94.5 to 105.5) is
  shifted -5 degrees, so adjacent sectors interlock with a ~9 mm staggered lap
  instead of a straight radial gap. 0.25 mm clearance on the mating faces.
* Door screw: 5.5 mm slot elongated +/-1 mm radially (covers the bolt-circle
  uncertainty), M5 hex nut pocket 8.3 mm across flats, 4.9 mm deep, on the fan
  face. The pocket is elongated with the slot so the nut can slide with the screw.
* Fan screw: 4.5 mm through hole with a 9 mm x 4.5 mm counterbore on the door
  face. A standard 10 mm fan screw then has 6.5 mm of thread in the fan corner.
* The nut pocket at r = 104 is fully recessed below the fan face, and the screw
  tip protrudes at r > 101.5, outside the fan frame's 100 mm half-width, so
  nothing touches the fan.

## Hardware

* 4 x M5 x 10 or M5 x 12 screws (button or socket head, black looks right next
  to the acrylic screws). The head sits on bare steel; the acrylic edge is
  about 5 mm away.
* 4 x M5 plain hex nuts (ISO 4032, 4.7 mm tall, fits; DIN 934 4.0 mm also fits;
  nyloc nuts do not).
* 4 x standard self-tapping fan screws (the ones in the NF-A20 box).

## Printing (A1 mini)

* Part is exported lying flat with the **fan face down** on the bed and the
  door face up, so the counterbores and rim relief are open pockets and the
  nut pocket is a short bridge over its ceiling. No supports.
* Footprint is 170 x 56 mm. If the slicer flags it as out of bounds, rotate it
  45 degrees on the plate (about 160 x 160 then). Two fit per plate rotated.
* PETG preferred (a fan-side screw hole in PLA is fine too). 0.2 mm layers,
  4 walls, 30 to 40 % infill. About 28 cm^3 (~35 g) per sector.
* Rotate the STL so the nut-pocket bridge sits along the print direction if you
  want it cleaner, but it is not structural.

## Assembly

1. Drop an M5 nut into each sector's hex pocket (fan face). A dab of glue keeps
   it there while handling.
2. Lay the four sectors on the NF-A20's intake side, interlocking the laps, and
   drive a fan screw through each counterbore into the fan's corner. The fan
   now holds the ring together as one piece.
3. Hold the fan+ring against the inside of the door with the four nut pockets
   over the top/bottom/left/right ring holes, and fit the four M5 screws from
   outside. The slots give +/-1 mm to find the holes.
4. Optional: a strip of 1 mm foam tape on the door face of the ring quiets
   vibration and seals the last gap.

Because the pattern is 90-degree symmetric you can rotate the whole fan to put
its cable at whichever corner suits the cable route.

## Tweaks

Everything is a named constant at the top of both sources. Things worth
changing if the first print shows a problem:

* `DOOR_BCD` if the door bolts land at the end of the slots (measure the
  centre-to-centre of two *opposite* orthogonal holes: it should be 208).
* `R_IN` if the fan frame's inner edge is not fully supported.
* `NUT_POCKET_DEPTH` / `NUT_AF` for a different nut.
* `RELIEF_R` if the outer rim still touches an acrylic screw head.
