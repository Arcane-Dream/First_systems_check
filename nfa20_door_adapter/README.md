# NF-A20 side-door fan adapter

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
