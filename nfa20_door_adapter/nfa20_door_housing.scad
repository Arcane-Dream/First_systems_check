// NF-A20 external door housing (v2) -- parametric OpenSCAD source.
// Same geometry as build_housing.py (which is the reference build).
// Frame: origin = cutout centre, x right / y up as seen from OUTSIDE the
// case, z = 0 at the steel's outer face, +z away from the case.
//
//   openscad -o flange.stl  -D 'part="flange"'        nfa20_door_housing.scad
//   openscad -o corner.stl  -D 'part="corner"'        nfa20_door_housing.scad
//   openscad -o cable.stl   -D 'part="corner_cable"'  nfa20_door_housing.scad
//   openscad -o bezel.stl   -D 'part="bezel"'         nfa20_door_housing.scad
//   openscad -o asm.stl     -D 'part="assembly"'      nfa20_door_housing.scad
// Single parts are exported already flipped for printing (print face on Z=0).

part = "assembly";

// ---- door (measured) --------------------------------------------------------
door_bcd     = 208;      // 8 holes at 0/45/90.. deg
cutout_d     = 187;
// ---- fan --------------------------------------------------------------------
fan_w        = 200;  fan_t = 30;  fan_hole_xy = 77;   // 154 mm pitch
// ---- flange plinth ----------------------------------------------------------
z_flange     = 14;
r_in         = 94.5;  r_out = 160;  r_mid = 105.5;
lap_half     = 5;     seam_gap = 0.25;
r_bear       = 112.5; relief_depth = 4.5;
r_deep       = 118;   deep_relief_depth = 12;
door_screw_d = 5.5;   door_play = 1.0;
nut_af       = 8.3;   nut_pocket = 6;
fan_screw_d  = 4.5;   fan_head_d = 8.6;
flange_cbore = z_flange - 3.5;
// ---- housing ----------------------------------------------------------------
wall = 3; clear = 2;
house_half   = fan_w / 2 + clear + wall;         // 105
house_r      = 8;
z_skirt      = z_flange + 0.5;
z_fan_top    = z_flange + fan_t;                 // 44
plate_t      = 5;
z_plate_top  = z_fan_top + plate_t;              // 49
plate_open_r = 95;
front_cbore  = 2.5;
grille_t     = 3;  grille_rings = [28, 50, 72];  grille_bar = 3;  grille_spokes = 16;
wall_lap     = 6;
tip_notch    = [7, 3];
cable_win    = 28;  cable_win_top = 36;
tie_slot     = [4, 3];  tie_slot_y = [66, 58];  tie_slot_z = 22;
// ---- bezel ------------------------------------------------------------------
mesh_t = 0.3;  bezel_t = 3.5;  bezel_open_r = 92;
magnet_d = 6.4;  magnet_h = 2.2;  magnet_r = 100;  magnet_angles = [5, 40];
bezel_a0 = 11.25;

$fn = 96;

module ann_sector(r1, r2, a0, a1, h, z0 = 0) {
    n = max(4, ceil(256 * (a1 - a0) / 360));
    pts = concat(
        [for (i = [0 : n]) let(a = a0 + (a1 - a0) * i / n) [r2 * cos(a), r2 * sin(a)]],
        [for (i = [0 : n]) let(a = a1 - (a1 - a0) * i / n) [r1 * cos(a), r1 * sin(a)]]);
    translate([0, 0, z0]) linear_extrude(h) polygon(pts);
}
module rsq(half, r, h, z0 = 0)
    translate([0, 0, z0]) linear_extrude(h) offset(r = r, $fn = 48) square(2 * (half - r), center = true);
module cylz(d, h, x = 0, y = 0, z = 0, fn = 48) translate([x, y, z]) cylinder(h = h, d = d, $fn = fn);
module hexz(af, h, x = 0, y = 0, z = 0) translate([x, y, z]) cylinder(h = h, r = af / sqrt(3), $fn = 6);
module boxz(x0, x1, y0, y1, z0, z1) translate([x0, y0, z0]) cube([x1 - x0, y1 - y0, z1 - z0]);
module radial_slot(r_c, ang, play) hull() for (d = [-play, play]) rotate(ang) translate([r_c + d, 0, 0]) children();

// ------------------------------------------------------------------ flange
module flange_sector() {
    a0 = -22.5; a1 = 67.5;
    g_out = (seam_gap / 2 / r_out) * 180 / PI;
    g_in  = (seam_gap / 2 / r_in)  * 180 / PI;
    difference() {
        intersection() {
            union() {
                ann_sector(r_mid + seam_gap / 2, r_out, a0 + lap_half + g_out, a1 + lap_half - g_out, z_flange);
                ann_sector(r_in, r_mid - seam_gap / 2, a0 - lap_half + g_in, a1 - lap_half - g_in, z_flange);
            }
            rsq(house_half, house_r, z_flange + 2, -1);
        }
        radial_slot(door_bcd / 2, 0, door_play) translate([0, 0, -1]) cylinder(h = z_flange + 2, d = door_screw_d, $fn = 48);
        radial_slot(door_bcd / 2, 0, door_play) translate([0, 0, z_flange - nut_pocket]) cylinder(h = nut_pocket + 1, r = nut_af / sqrt(3), $fn = 6);
        cylz(fan_screw_d, z_flange + 2, fan_hole_xy, fan_hole_xy, -1);
        cylz(fan_head_d, flange_cbore + 1, fan_hole_xy, fan_hole_xy, -1);
        ann_sector(r_bear, r_out + 1, a0 - 20, a1 + 20, relief_depth + 1, -1);
        ann_sector(r_deep, r_out + 1, a0 - 20, a1 + 20, deep_relief_depth + 1, -1);
    }
}

// ----------------------------------------------------------------- housing
module grille_full() {
    for (r = grille_rings) ann_sector(r - grille_bar / 2, r + grille_bar / 2, 0, 360, grille_t, z_plate_top - grille_t);
    r0 = grille_rings[0] - grille_bar / 2;
    for (i = [0 : grille_spokes - 1]) rotate(360 * i / grille_spokes)
        boxz(r0, plate_open_r + 1.5, -grille_bar / 2, grille_bar / 2, z_plate_top - grille_t, z_plate_top);
}
module housing_full() {
    difference() {
        rsq(house_half, house_r, z_plate_top - z_skirt, z_skirt);
        rsq(house_half - wall, house_r - wall, z_fan_top - z_skirt + 0.01, z_skirt - 0.01);
        cylz(2 * plate_open_r, plate_t + 2, 0, 0, z_fan_top - 1, 256);
    }
    grille_full();
}
module housing_corner(cable = false) {
    g = seam_gap / 2;
    zb = z_skirt - 0.01; zt = z_fan_top;
    xi = house_half - wall; xm = house_half - wall / 2; xo = house_half;
    difference() {
        union() {
            intersection() { housing_full(); boxz(g, house_half + 2, g, house_half + 2, 0, z_plate_top + 1); }
            boxz(xm + g, xo, -wall_lap, g, z_skirt, zt);        // right wall outer half, extended
            boxz(-wall_lap, g, xi, xm - g, z_skirt, zt);        // top wall inner half, extended
        }
        boxz(xi - 1, xm + g, -1, wall_lap + g, zb, zt);          // right wall inner half, cut back
        boxz(-1, wall_lap + g, xm + g, xo + 1, zb, zt);          // top wall outer half, cut back
        boxz(xi - 1, xo + 1, -tip_notch[0], tip_notch[0], zb, z_skirt + tip_notch[1]);
        boxz(-tip_notch[0], tip_notch[0], xi - 1, xo + 1, zb, z_skirt + tip_notch[1]);
        cylz(fan_screw_d, plate_t + 2, fan_hole_xy, fan_hole_xy, z_fan_top - 1);
        cylz(fan_head_d, front_cbore + 1, fan_hole_xy, fan_hole_xy, z_plate_top - front_cbore);
        for (a = magnet_angles) cylz(magnet_d, magnet_h + 1, magnet_r * cos(a), magnet_r * sin(a), z_plate_top - magnet_h);
        if (cable) {
            w0 = house_half - cable_win;
            boxz(w0, house_half + 1, w0, house_half + 1, z_skirt - 1, cable_win_top);
            for (y = tie_slot_y) boxz(xi - 1, xo + 1, y - tie_slot[0] / 2, y + tie_slot[0] / 2,
                                      tie_slot_z - tie_slot[1] / 2, tie_slot_z + tie_slot[1] / 2);
        }
    }
}

// ------------------------------------------------------------------- bezel
module bezel_sector() {
    z0 = z_plate_top + mesh_t;
    a0 = bezel_a0; a1 = bezel_a0 + 90;
    g0 = a0 + (seam_gap / 2 / 100) * 180 / PI;
    g1 = a1 - (seam_gap / 2 / 100) * 180 / PI;
    big = 400;
    difference() {
        intersection() {
            difference() { rsq(house_half, house_r, bezel_t, z0); cylz(2 * bezel_open_r, bezel_t + 2, 0, 0, z0 - 1, 256); }
            translate([0, 0, z0 - 1]) linear_extrude(bezel_t + 2)
                polygon([[0, 0], [big * cos(g0), big * sin(g0)], [big * cos((g0 + g1) / 2), big * sin((g0 + g1) / 2)], [big * cos(g1), big * sin(g1)]]);
        }
        for (a = [magnet_angles[1], magnet_angles[0] + 90])
            cylz(magnet_d, magnet_h + 1, magnet_r * cos(a), magnet_r * sin(a), z0 - 1);
    }
}

// ------------------------------------------------------------------ output
module flip(z_top) rotate([180, 0, 0]) translate([0, 0, -z_top]) children();

if (part == "flange")            flip(z_flange) rotate(-22.5) flange_sector();
else if (part == "corner")       flip(z_plate_top) housing_corner(false);
else if (part == "corner_cable") flip(z_plate_top) housing_corner(true);
else if (part == "bezel")        flip(z_plate_top + mesh_t + bezel_t) rotate(-(bezel_a0 + 45)) bezel_sector();
else for (k = [0 : 3]) rotate(90 * k) { flange_sector(); housing_corner(k == 2); bezel_sector(); }
