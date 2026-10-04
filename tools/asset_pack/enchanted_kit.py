"""Companion forest library: dreaming trees, painted insects and scenic animals.

Explicit authoring only. The original forest library is never regenerated here.
Critters are static environment decorations, facing -Y with a ground-zero pivot;
insects use a body-centered flight pivot so they can also be perched or scattered.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from mathutils import Matrix, Vector
import art_style as style
import geometry as g
import forest_kit as forest
import painted_finish as paint

LIBRARY = g.ROOT / 'sources/environment/shared_enchanted_kit.blend'
PROTOTYPES = {}


def reset():
    PROTOTYPES.clear()
    forest.reset()


def place(kind, pos=(0, 0, 0), scale=1, rotation=(0, 0, 0)):
    return forest.place(kind, pos, scale, rotation, library=LIBRARY, prototypes=PROTOTYPES)


def organic(name, pos, size, material):
    obj = g.ico(name, pos, size, material, 3, 0)
    # Round flesh and soft fur; wood, wings and shell facets remain broad planes.
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def buttresses(material):
    for i in range(5):
        a = i * math.tau / 5 + .25
        g.tube('Splayed dreaming tree root', [(0, 0, .35),
               (.46 * math.cos(a), .46 * math.sin(a), .13),
               (.88 * math.cos(a), .88 * math.sin(a), .035)],
               [.22, .13, .035], material, 8)


def hollow_tree():
    buttresses('bark_haunted')
    # Split front timbers and a rear trunk leave a real recessed mouth opening.
    g.tube('Hollow watcher rear trunk', [(0, .20, .20), (.06, .27, 1.14),
           (-.12, .22, 2.02), (.10, .13, 2.66)], [.36, .34, .26, .10], 'bark_haunted', 9)
    for side in (-1, 1):
        g.tube('Hollow watcher cheek timber', [(side * .23, -.15, .19),
               (side * .39, -.19, .70), (side * .32, -.21, 1.24),
               (side * .17, -.10, 1.62)], [.22, .16, .14, .20], 'bark_haunted_light', 8)
        g.tube('Raised wooden brow', [(side * .06, -.23, 1.67),
               (side * .23, -.33, 1.83), (side * .41, -.24, 1.76)],
               [.09, .12, .045], 'bark_haunted', 7)
        organic('Watchful recessed eye', (side * .23, -.315, 1.69), (.09, .025, .055), 'gill_glow')
        g.tube('Crooked reaching bough', [(side * .12, .05, 1.48),
               (side * .64, .10, 1.87), (side * .98, .06, 2.26),
               (side * 1.16, -.03, 2.53), (side * .98, -.08, 2.66)],
               [.17, .14, .10, .055, .018], 'bark_haunted', 8)
        g.tube('Forked reaching twig', [(side * .70, .08, 1.99),
               (side * .82, -.18, 2.30), (side * .65, -.27, 2.44)],
               [.085, .049, .012], 'bark_haunted_light', 7)
    # A coiled broken crown makes the silhouette stranger than a normal snag.
    crown = [(.10 + (.37 - .014 * i) * math.cos(i * .30), .12,
              2.67 + (.37 - .014 * i) * math.sin(i * .30)) for i in range(19)]
    g.tube('Watcher spiral crown', [(0, .17, 2.22), *crown],
           [.14, *[.10 * (1 - i / 21) for i in range(19)]], 'bark_haunted_light', 8)
    for x, z, scale in [(-.33, .43, .20), (.39, 1.11, .16), (-.91, 2.23, .10)]:
        # Familiar kit mushrooms nestled against the new wood.
        before = set(g.CURRENT.objects)
        forest.mushroom(True)
        transform = Matrix.Translation((x, -.13, z)) @ Matrix.Scale(scale, 4)
        for obj in set(g.CURRENT.objects) - before:
            obj.data.transform(transform)


def leaf(name, origin, tip, width, material):
    origin, tip = Vector(origin), Vector(tip)
    direction = tip - origin
    across = Vector((direction.y, -direction.x, 0))
    if across.length < .001:
        across = Vector((1, 0, 0))
    across.normalize()
    middle = origin + direction * .52
    verts = [origin, middle - across * width, middle + Vector((0, -.055, .045)),
             middle + across * width, tip]
    obj = g.mesh(name, verts, [(0, 1, 2), (0, 2, 3), (1, 4, 2), (2, 4, 3)], material)
    uv = obj.data.uv_layers.new(name=style.TEXTURES.uv_name)
    coords = [(.5, 0), (0, .52), (.5, .52), (1, .52), (.5, 1)]
    for poly in obj.data.polygons:
        poly.use_smooth = True
        for index in poly.loop_indices:
            uv.data[index].uv = coords[obj.data.loops[index].vertex_index]
    return obj


def spiral_tree():
    buttresses('bark')
    trunk = [(0, 0, .05), (-.17, .09, .86), (.12, .07, 1.56), (-.16, .03, 2.20)]
    spiral = [(-.16 + .66 * math.sin(i * .24), .02 + .06 * math.sin(i * .6),
               2.89 - .66 * math.cos(i * .24)) for i in range(25)]
    g.tube('Dream willow coiling trunk', [*trunk, *spiral],
           [.35, .29, .22, .17, *[.16 * (1 - i / 28) for i in range(25)]], 'bark', 9)
    for side in (-1, 1):
        g.tube('Dream willow arching branch', [(0, .07, 1.61), (side * .59, .09, 2.11),
               (side * 1.03, .07, 2.24), (side * 1.28, -.01, 1.99)],
               [.16, .115, .075, .026], 'bark_light', 8)
        for j in range(4):
            x = side * (.45 + .23 * j)
            z = 2.14 - .025 * j * j
            g.tube('Willow hanging tendril', [(x, .02, z), (x + side * .07, -.025, z - .35),
                   (x - side * .025, -.06, z - .76)], [.014, .011, .004], 'forest_leaf_teal', 6)
            for k in range(3):
                leaf('Drooping teal willow leaf', (x, -.03, z - .18 - k * .19),
                     (x + side * (.18 - k * .02), -.10, z - .49 - k * .19),
                     .077, 'forest_leaf_teal' if (j + k) % 2 else 'forest_leaf_lilac')
            organic('Willow luminous seed', (x - side * .025, -.06, z - .78),
                    (.031, .028, .062), 'gill_glow')
    for i in range(7):
        p = spiral[i * 3 + 2]
        leaf('Spiral crown lilac leaf', p, (p[0] + .24, p[1] - .10, p[2] + .25), .12, 'forest_leaf_lilac')


def wing(outline, side, material, lift):
    # A shallow closed volume survives viewing from below; no alpha sorting.
    points = [(side * x, y, lift * x) for x, y in outline]
    center = tuple(sum(p[axis] for p in points) / len(points) for axis in range(3))
    verts = [center, *points, *((x, y, z - .015) for x, y, z in [center, *points])]
    n = len(points) + 1
    faces = []
    for i in range(1, n):
        j = i + 1 if i + 1 < n else 1
        faces.extend([(0, i, j), (n, n + j, n + i), (i, n + i, n + j, j)])
    obj = g.mesh('Painted butterfly wing', verts, faces, material)
    obj.data.materials.append(g.M['wing_border'])
    uv = obj.data.uv_layers.new(name=style.TEXTURES.uv_name)
    for poly in obj.data.polygons:
        if poly.index % 3 == 2:
            poly.material_index = 1
        for index in poly.loop_indices:
            p = obj.data.vertices[obj.data.loops[index].vertex_index].co
            uv.data[index].uv = (.5 + p.y / 1.6, abs(p.x) / .85)


def butterfly(material='wing_cyan', moth=False):
    fore = [(.04, -.14), (.18, -.44), (.37, -.62), (.54, -.67), (.71, -.62),
            (.82, -.49), (.85, -.32), (.78, -.16), (.59, .07), (.12, .13)]
    hind = [(.06, .06), (.40, .02), (.57, .10), (.66, .23), (.63, .36),
            (.51, .49), (.34, .54), (.18, .45), (.10, .31)]
    if moth:
        fore = [(.04, -.12), (.27, -.40), (.74, -.45), (.88, -.21), (.72, .06), (.17, .19)]
        hind = [(.05, .11), (.57, .12), (.65, .35), (.35, .77), (.29, .36), (.10, .32)]
    for side in (-1, 1):
        wing(fore, side, material, .29 if moth else .39)
        wing(hind, side, material if moth else 'wing_lilac', .25 if moth else .34)
        g.tube('Curled butterfly antenna', [(side * .045, -.25, .05),
               (side * .13, -.43, .13), (side * .20, -.44, .15)], [.015, .009, .004], 'wing_border', 6)
    organic('Velvet insect abdomen', (0, .12, .025), (.055, .23, .052), 'fur_cream' if moth else 'wing_border')
    organic('Velvet insect thorax', (0, -.13, .05), (.077, .13, .075), 'fur_cream' if moth else 'fur_teal')
    organic('Insect head', (0, -.27, .067), (.065, .065, .062), 'wing_border')


def jackalope():
    organic('Round jackalope haunch', (0, .20, .34), (.30, .35, .33), 'fur_lavender')
    organic('Jackalope cream chest', (0, -.13, .34), (.23, .22, .28), 'fur_cream')
    organic('Jackalope head', (0, -.30, .65), (.25, .22, .24), 'fur_lavender')
    for side in (-1, 1):
        organic('Rabbit front paw', (side * .15, -.27, .075), (.10, .18, .075), 'fur_cream')
        organic('Rabbit rear paw', (side * .24, .19, .09), (.13, .22, .09), 'fur_lavender')
        ear = organic('Long jackalope ear', (side * .16, -.20, 1.02), (.083, .067, .33), 'fur_lavender')
        inner = organic('Soft inner rabbit ear', (side * .16, -.257, 1.04), (.047, .015, .23), 'fur_coral')
        transform = Matrix.Translation((side * .16, -.20, .79))
        for obj in (ear, inner):
            obj.data.transform(transform @ Matrix.Rotation(-side * .17, 4, 'Y') @ transform.inverted())
        organic('Bright rabbit eye', (side * .18, -.464, .70), (.052, .031, .06), 'black')
        organic('Rabbit eye catchlight', (side * .178, -.490, .722), (.014, .008, .016), 'cream')
        organic('Plump rabbit muzzle', (side * .067, -.502, .59), (.078, .052, .063), 'fur_cream')
        g.tube('Tiny branching antler', [(side * .19, -.04, .77), (side * .30, .0, 1.04),
               (side * .42, -.035, 1.27), (side * .39, -.075, 1.41)], [.039, .031, .021, .009], 'wood_edge', 7)
        g.tube('Antler fork', [(side * .31, 0, 1.07), (side * .21, .02, 1.27)], [.025, .007], 'wood_edge', 7)
    organic('Small rabbit nose', (0, -.553, .62), (.035, .021, .025), 'fur_coral')
    organic('Round cotton tail', (0, .51, .36), (.14, .13, .14), 'fur_cream')


def lantern_snail():
    organic('Snail soft foot', (0, 0, .10), (.23, .57, .10), 'fur_teal')
    organic('Snail rising neck', (0, -.35, .26), (.16, .21, .24), 'fur_teal')
    organic('Snail round head', (0, -.48, .40), (.18, .15, .13), 'fur_teal')
    # Broad closed shell, with a flush spiral band rather than fine modeled grooves.
    organic('Coral lantern shell', (0, .12, .44), (.30, .34, .36), 'fur_coral')
    points = [(.285, .12 + (.26 - i * .005) * math.cos(i * .22),
               .44 + (.26 - i * .005) * math.sin(i * .22)) for i in range(45)]
    g.tube('Snail shell broad spiral', points, .023, 'fur_cream', 7)
    for side in (-1, 1):
        g.tube('Snail eyestalk', [(side * .085, -.51, .45),
               (side * .13, -.57, .61), (side * .17, -.57, .70)], [.025, .020, .014], 'fur_teal', 8)
        organic('Snail dark eye', (side * .17, -.578, .70), (.027, .022, .028), 'black')
    organic('Shell lantern seed', (0, .12, .84), (.073, .067, .11), 'window_hot')
    for i in range(4):
        a = i * math.tau / 4
        leaf('Lantern seed calyx', (.04 * math.cos(a), .12 + .04 * math.sin(a), .81),
             (.12 * math.cos(a), .12 + .12 * math.sin(a), .90), .045, 'forest_leaf_lilac')


def lantern_flower():
    g.tube('Curled lantern flower stem', [(0, 0, 0), (-.12, .02, .42),
           (.02, .0, .84), (.27, -.02, .98), (.38, -.02, .85)],
           [.035, .03, .022, .018, .012], 'forest_leaf_teal', 8)
    for side in (-1, 1):
        leaf('Lantern flower broad leaf', (-.06, 0, .25),
             (side * .38, -.07, .43), .15, 'forest_leaf_teal')
    organic('Lantern flower warm heart', (.38, -.02, .69), (.11, .10, .14), 'window_hot')
    for i in range(5):
        a = i * math.tau / 5
        leaf('Hanging lilac lantern petal', (.38, -.02, .84),
             (.38 + .20 * math.cos(a), -.02 + .20 * math.sin(a), .57),
             .10, 'forest_leaf_lilac')


def spiral_fern():
    for i in range(3):
        angle = (i - 1) * .72
        transform = Matrix.Rotation(angle, 4, 'Z')
        points = [(0, 0, .02), (.09, 0, .37)]
        points += [(.10 + (.19 - j * .005) * math.cos(j * .25), 0,
                    .66 + (.19 - j * .005) * math.sin(j * .25)) for j in range(24)]
        g.tube('Dream fern curled frond', [transform @ Vector(p) for p in points],
               [.034, .029, *[.027 * (1 - j / 29) for j in range(24)]], 'forest_leaf_lilac', 7)
        for j in range(3):
            for side in (-1, 1):
                leaf('Dream fern teal leaflet', transform @ Vector((.05, 0, .20 + j * .13)),
                     transform @ Vector((side * (.22 - j * .035), .07, .31 + j * .14)),
                     .064, 'forest_leaf_teal')


BUILDERS = {
    'hollow_tree': hollow_tree,
    'spiral_tree': spiral_tree,
    'butterfly_cyan': butterfly,
    'butterfly_sunset': lambda: butterfly('wing_coral'),
    'moon_moth': lambda: butterfly('wing_moon', True),
    'jackalope': jackalope,
    'lantern_snail': lantern_snail,
    'lantern_flower': lantern_flower,
    'spiral_fern': spiral_fern,
}


def main():
    g.clear_scene()
    reset()
    for i, (kind, builder) in enumerate(BUILDERS.items()):
        col = g.collection('forest_' + kind)
        g.target(col)
        builder()
        for obj in col.objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                for mod in list(obj.modifiers):
                    bpy.ops.object.modifier_apply(modifier=mod.name)
        paint.apply(col)
        col.asset_mark()
        col.asset_data.description = 'Painted dreaming forest component: ' + kind
        col['placement_origin'] = 'body-centered flight pivot' if kind.startswith(('butterfly', 'moon_moth')) else 'ground-zero; forward -Y'
        col['animation_policy'] = 'static scenic decoration'
        col.use_fake_user = True
        bpy.context.scene.collection.children.unlink(col)
        display = bpy.data.objects.new('Display ' + kind, None)
        bpy.context.scene.collection.objects.link(display)
        display.instance_type = 'COLLECTION'
        display.instance_collection = col
        display.location = ((i % 3 - 1) * 4, (1 - i // 3) * 4, 0)
    g.studio(1.0, 16)
    bpy.ops.wm.save_as_mainfile(filepath=str(LIBRARY))
    print('Saved', len(BUILDERS), 'companion forest components', flush=True)


if __name__ == '__main__':
    main()
