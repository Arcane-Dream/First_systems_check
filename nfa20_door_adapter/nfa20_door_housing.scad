// NF-A20 external door housing (v3, round) -- parametric OpenSCAD source.
// Same geometry as build_housing.py (the reference build).
// Frame: origin = cutout centre, x right / y up as seen from OUTSIDE the
// case, z = 0 at the steel's outer face, +z away from the case.
//
//   openscad -o flange.stl -D 'part="flange"'   nfa20_door_housing.scad
//   openscad -o inner.stl  -D 'part="inner"'    nfa20_door_housing.scad
//   openscad -o quad.stl   -D 'part="quadrant"' nfa20_door_housing.scad
//   openscad -o bezel.stl  -D 'part="bezel"'    nfa20_door_housing.scad
//   openscad -o asm.stl    -D 'part="assembly"' nfa20_door_housing.scad
// Single parts are exported already flipped for printing (print face on Z=0).

part = "assembly";

// ---- door (measured) --------------------------------------------------------
door_bcd       = 208;   cutout_d = 187;   steel_t = 0.86;
acrylic_edge_r = 114.7;
// ---- fan --------------------------------------------------------------------
fan_w = 200;  fan_t = 30;  fan_hole_xy = 77;
// ---- plinth -------------------------------------------------------------------
z_flange = 14;  r_in = 90.7;  r_out = acrylic_edge_r - 0.7;  r_mid = 103;
lap_half = 5;   seam_gap = 0.25;
r_bear = 112.5; relief_depth = 4.5;
collar_od = 185.8;  collar_chamfer = 0.8;
door_screw_d = 5.5; door_play = 1.0;  nut_af = 8.3;  nut_pocket = 6;
fan_tap_d = 3.6;  fan_hole_depth = 12;
fan_insert = false;  fan_insert_d = 5.6;  fan_insert_h = 8;
inner_t = 8;  inner_r_in = collar_od / 2 + 0.25;  inner_r_out = 117;
inner_r_bear = 113;  inner_relief = 1.5;  inner_cbore_d = 9.5;  inner_cbore = 4;
collar_h = steel_t + inner_t + 0.5;
// ---- housing ----------------------------------------------------------------
wall = 3;  skirt_r_out = r_out;  skirt_r_in = skirt_r_out - wall;
z_skirt = z_flange + 0.5;  z_fan_top = z_flange + fan_t;
plate_t = 5;  z_plate_top = z_fan_top + plate_t;  plate_r = 117;  plate_open_r = 95;
fan_screw_d = 4.5;  fan_head_d = 7.6;  front_cbore = 2.5;
grille_t = 3;  grille_rings = [28, 50, 72];  grille_bar = 3;  grille_spokes = 16;
wall_lap_deg = 3;  window_clear_deg = 1.5;  tongue_top_gap = 0.3;
tie_slot = [4, 3];  tie_slot_angles = [14, 19];  tie_slot_z = 22;
// ---- bezel ------------------------------------------------------------------
mesh_t = 0.3;  bezel_t = 3.5;  bezel_r = plate_r;  bezel_open_r = 92;
magnet_d = 6.4;  magnet_h = 2.2;  magnet_r = 100;  magnet_angles = [5, 40];  bezel_a0 = 11.25;

$fn = 96;
function deg_at(r, mm) = mm / r * 180 / PI;

module ann_sector(r1, r2, a0, a1, h, z0 = 0) {
    n = max(4, ceil(256 * (a1 - a0) / 360));
    pts = concat(
        [for (i = [0 : n]) let(a = a0 + (a1 - a0) * i / n) [r2 * cos(a), r2 * sin(a)]],
        [for (i = [0 : n]) let(a = a1 - (a1 - a0) * i / n) [r1 * cos(a), r1 * sin(a)]]);
    translate([0, 0, z0]) linear_extrude(h) polygon(pts);
}
module ring(r1, r2, h, z0 = 0) translate([0, 0, z0]) difference() { cylinder(h = h, r = r2, $fn = 256); translate([0, 0, -1]) cylinder(h = h + 2, r = r1, $fn = 256); }
module cylz(d, h, x = 0, y = 0, z = 0, fn = 48) translate([x, y, z]) cylinder(h = h, d = d, $fn = fn);
module boxz(x0, x1, y0, y1, z0, z1) translate([x0, y0, z0]) cube([x1 - x0, y1 - y0, z1 - z0]);
module radial_slot(r_c, ang, play) hull() for (d = [-play, play]) rotate(ang) translate([r_c + d, 0, 0]) children();

// one sector of a lap-split ring, as a single solid (bands overlap inside the body)
module lapped_sector(r1, r2, rm, a0, a1, lap, gap, h, z0 = 0) {
    g_in = deg_at(r1, gap / 2); g_out = deg_at(r2, gap / 2); g_mid = deg_at(rm, gap / 2);
    difference() {
        ann_sector(r1, rm + 1, a0 - lap + g_in, a1 - lap - g_in, h, z0);
        ann_sector(rm - gap / 2, rm + 2, a0 - lap - 1, a0 + lap + g_mid, h + 2, z0 - 1);
    }
    difference() {
        ann_sector(rm - 1, r2, a0 + lap + g_out, a1 + lap - g_out, h, z0);
        ann_sector(rm - 2, rm + gap / 2, a1 - lap - g_mid, a1 + lap + 1, h + 2, z0 - 1);
    }
}

// ------------------------------------------------------------------ plinth
module flange_sector() {
    a0 = -22.5; a1 = 67.5; r_co = collar_od / 2; g_in = deg_at(r_in, seam_gap / 2);
    difference() {
        union() {
            lapped_sector(r_in, r_out, r_mid, a0, a1, lap_half, seam_gap, z_flange);
            ann_sector(r_in, r_co, a0 - lap_half + g_in, a1 - lap_half - g_in, collar_h + 0.5, -collar_h);
        }
        difference() {   // collar lead-in chamfer (cone extended past the cutter so no full slice is cut)
            cylz(2 * r_co + 2, collar_chamfer + 0.01, 0, 0, -collar_h - 0.01, 256);
            translate([0, 0, -collar_h - 0.1]) cylinder(h = collar_chamfer + 0.2, r1 = r_co - collar_chamfer - 0.1, r2 = r_co + 0.1, $fn = 256);
        }
        radial_slot(door_bcd / 2, 0, door_play) translate([0, 0, -1]) cylinder(h = z_flange + 2, d = door_screw_d, $fn = 48);
        radial_slot(door_bcd / 2, 0, door_play) translate([0, 0, z_flange - nut_pocket]) cylinder(h = nut_pocket + 1, r = nut_af / sqrt(3), $fn = 6);
        if (fan_insert) {
            cylz(fan_insert_d, fan_insert_h + 1, fan_hole_xy, fan_hole_xy, z_flange - fan_insert_h);
            cylz(fan_tap_d + 0.6, fan_hole_depth + 1, fan_hole_xy, fan_hole_xy, z_flange - fan_hole_depth);
        } else cylz(fan_tap_d, fan_hole_depth + 1, fan_hole_xy, fan_hole_xy, z_flange - fan_hole_depth);
        ann_sector(r_bear, r_out + 1, a0 - 20, a1 + 20, relief_depth + 1, -1);
    }
}

// -------------------------------------------------------------- inner ring
module inner_ring_sector() {
    a0 = -45; a1 = 45; z0 = -steel_t - inner_t;
    difference() {
        lapped_sector(inner_r_in, inner_r_out, r_mid, a0, a1, lap_half, seam_gap, inner_t, z0);
        radial_slot(door_bcd / 2, 0, door_play) translate([0, 0, z0 - 1]) cylinder(h = inner_t + 2, d = door_screw_d, $fn = 48);
        radial_slot(door_bcd / 2, 0, door_play) translate([0, 0, z0 - 1]) cylinder(h = inner_cbore + 1, d = inner_cbore_d, $fn = 48);
        ann_sector(inner_r_bear, inner_r_out + 1, a0 - 20, a1 + 20, inner_relief + 1, -steel_t - inner_relief);
    }
}

// ----------------------------------------------------------------- housing
function window_half() = 45 - atan2(sqrt(skirt_r_in * skirt_r_in - (fan_w / 2) * (fan_w / 2)), fan_w / 2) + window_clear_deg;

module grille_quadrant() {
    g = seam_gap / 2;
    intersection() {
        union() {
            for (r = grille_rings) ring(r - grille_bar / 2, r + grille_bar / 2, grille_t, z_plate_top - grille_t);
            r0 = grille_rings[0] - grille_bar / 2;
            for (i = [0 : grille_spokes - 1]) let(a = 360 * i / grille_spokes) if (a <= 95 || a >= 355)
                rotate(a) boxz(r0, plate_open_r + 1.5, -grille_bar / 2, grille_bar / 2, z_plate_top - grille_t, z_plate_top);
        }
        boxz(g, 200, g, 200, 0, 100);
    }
}

module housing_quadrant() {
    gp = deg_at(plate_open_r, seam_gap / 2);
    w = window_half();
    gi = deg_at(skirt_r_in, seam_gap / 2); gm = deg_at(skirt_r_in + wall / 2, seam_gap / 2); go = deg_at(skirt_r_out, seam_gap / 2);
    r_m = skirt_r_in + wall / 2;
    hz = z_fan_top - z_skirt;
    difference() {
        union() {
            ann_sector(plate_open_r, plate_r, gp, 90 - gp, plate_t, z_fan_top);
            grille_quadrant();
            // arc at the 0 deg seam: outer half extends past the seam, inner half starts after the lap
            ann_sector(r_m + seam_gap / 2, skirt_r_out, -wall_lap_deg + go, 45 - w, hz, z_skirt);
            difference() {
                ann_sector(skirt_r_in, r_m + 1, wall_lap_deg + gm, 45 - w, hz, z_skirt);
                ann_sector(r_m - seam_gap / 2, r_m + 2, -1, wall_lap_deg + gm, hz + 2, z_skirt - 1);
            }
            // arc at the 90 deg seam: inner half extends past the seam, outer half stops short
            ann_sector(skirt_r_in, r_m - seam_gap / 2, 45 + w, 90 + wall_lap_deg - gi, hz, z_skirt);
            difference() {
                ann_sector(r_m - 1, skirt_r_out, 45 + w, 90 - wall_lap_deg - gm, hz, z_skirt);
                ann_sector(r_m - 2, r_m + seam_gap / 2, 90 - wall_lap_deg - gm, 91, hz + 2, z_skirt - 1);
            }
        }
        ann_sector(skirt_r_in - 1, skirt_r_out + 1, -wall_lap_deg - 1, 0, tongue_top_gap + 1, z_fan_top - tongue_top_gap);
        ann_sector(skirt_r_in - 1, skirt_r_out + 1, 90, 90 + wall_lap_deg + 1, tongue_top_gap + 1, z_fan_top - tongue_top_gap);
        cylz(fan_screw_d, plate_t + 2, fan_hole_xy, fan_hole_xy, z_fan_top - 1);
        cylz(fan_head_d, front_cbore + 1, fan_hole_xy, fan_hole_xy, z_plate_top - front_cbore);
        for (a = magnet_angles) cylz(magnet_d, magnet_h + 1, magnet_r * cos(a), magnet_r * sin(a), z_plate_top - magnet_h);
        for (a = tie_slot_angles) let(da = deg_at(r_m, tie_slot[0]) / 2)
            ann_sector(skirt_r_in - 1, skirt_r_out + 1, a - da, a + da, tie_slot[1], tie_slot_z - tie_slot[1] / 2);
    }
}

// ------------------------------------------------------------------- bezel
module bezel_sector() {
    z0 = z_plate_top + mesh_t; g = deg_at(bezel_open_r, seam_gap / 2);
    difference() {
        ann_sector(bezel_open_r, bezel_r, bezel_a0 + g, bezel_a0 + 90 - g, bezel_t, z0);
        for (a = [magnet_angles[1], magnet_angles[0] + 90]) cylz(magnet_d, magnet_h + 1, magnet_r * cos(a), magnet_r * sin(a), z0 - 1);
    }
}

// ------------------------------------------------------------------ output
module flip(z_top) rotate([180, 0, 0]) translate([0, 0, -z_top]) children();

if (part == "flange")        flip(z_flange) rotate(-22.5) flange_sector();
else if (part == "inner")    flip(-steel_t) inner_ring_sector();
else if (part == "quadrant") flip(z_plate_top) rotate(-45) housing_quadrant();
else if (part == "bezel")    flip(z_plate_top + mesh_t + bezel_t) rotate(-(bezel_a0 + 45)) bezel_sector();
else for (k = [0 : 3]) rotate(90 * k) { flange_sector(); inner_ring_sector(); housing_quadrant(); bezel_sector(); }
