// NF-A20 -> case-door adapter ring (parametric OpenSCAD source)
//
// Same geometry as build_adapter.py.  Origin = centre of the door's round
// cutout, +Z into the case.  One 90-degree sector is exported; print 4.
//
//   openscad -o sector.stl -D 'part="sector"'  nfa20_door_adapter.scad
//   openscad -o asm.stl    -D 'part="assembly"' nfa20_door_adapter.scad

part = "sector";          // "sector" | "assembly"

// ---- door (measured, converted to metric) --------------------------------
door_bcd      = 208;      // 8 holes, 45 deg apart, measured 207.7
door_hole_d   = 5.8;
cutout_d      = 187;

// ---- fan: Noctua NF-A20 ---------------------------------------------------
fan_pitch     = 154;      // hole square
fan_hole_xy   = fan_pitch / 2;   // hole at (77, 77) -> r = 108.9 @ 45 deg

// ---- adapter ----------------------------------------------------------------
T             = 8;
r_in          = 94.5;
r_out         = 117;
r_mid         = 105.5;
lap_half      = 5;        // deg
seam_gap      = 0.25;

door_screw_d  = 5.5;      // M5 clearance
door_play     = 1.0;      // +/- radial slot
nut_af        = 8.0 + 0.3;
nut_pocket    = 4.7 + 0.2;

fan_screw_d   = 4.5;
fan_cbore_d   = 9.0;
fan_cbore_h   = 4.5;

relief_r      = 113;
relief_h      = 1.5;

$fn = 96;

module ann_sector(r1, r2, a0, a1, h, z0 = 0) {
    n = max(4, ceil(256 * (a1 - a0) / 360));
    pts = concat(
        [for (i = [0 : n]) let(a = a0 + (a1 - a0) * i / n) [r2 * cos(a), r2 * sin(a)]],
        [for (i = [0 : n]) let(a = a1 - (a1 - a0) * i / n) [r1 * cos(a), r1 * sin(a)]]);
    translate([0, 0, z0]) linear_extrude(h) polygon(pts);
}

module hex_prism(af, h) cylinder(h = h, r = af / sqrt(3), $fn = 6);

module radial_slot(r_c, ang, play) {
    hull() for (d = [-play, play])
        rotate(ang) translate([r_c + d, 0, 0]) children();
}

module sector() {
    a0 = -22.5; a1 = 67.5;
    g_out = (seam_gap / 2 / r_out) * 180 / PI;
    g_in  = (seam_gap / 2 / r_in)  * 180 / PI;
    difference() {
        union() {
            ann_sector(r_mid + seam_gap / 2, r_out, a0 + lap_half + g_out, a1 + lap_half - g_out, T);
            ann_sector(r_in, r_mid - seam_gap / 2, a0 - lap_half + g_in, a1 - lap_half - g_in, T);
        }
        // door screw slot (through) + nut pocket on the fan face (z = 0)
        radial_slot(door_bcd / 2, 0, door_play) translate([0, 0, -1]) cylinder(h = T + 2, d = door_screw_d);
        radial_slot(door_bcd / 2, 0, door_play) translate([0, 0, -1]) hex_prism(nut_af, nut_pocket + 1);
        // fan screw: through hole + counterbore on the door face (z = T)
        translate([fan_hole_xy, fan_hole_xy, -1]) cylinder(h = T + 2, d = fan_screw_d);
        translate([fan_hole_xy, fan_hole_xy, T - fan_cbore_h]) cylinder(h = fan_cbore_h + 1, d = fan_cbore_d);
        // rim relief on the door face (clears acrylic-window screw heads)
        ann_sector(relief_r, r_out + 1, a0 - 20, a1 + 20, relief_h + 1, T - relief_h);
    }
}

if (part == "sector") rotate(-22.5) sector();
else for (k = [0 : 3]) rotate(90 * k) sector();
