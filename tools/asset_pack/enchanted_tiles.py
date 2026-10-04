"""Three dreaming forest hexes, composed from the two reusable forest libraries."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import art_style as style
import geometry as g
import forest_kit as forest
import enchanted_kit as dream
import painted_finish as paint

# kind, local position, scale, Z rotation; geometry stays in the libraries.
RECIPES = {
    'hex_hollow_watchers': [
        ('hollow_tree', (-.15, .35, 0), 1.05, -.08),
        ('mushroom_purple', (-1.08, -.38, 0), .52, .3),
        ('mushroom_blue', (.88, -.39, 0), .43, .8),
        ('crystal_purple', (-.95, .72, 0), .43, .4),
        ('boulder', (.86, .68, 0), .76, .1),
        ('spiral_fern', (-.75, -1.07, 0), .77, -.4),
        ('lantern_flower', (.67, -.94, 0), .80, .4),
        ('moon_moth', (-.66, -.21, 2.13), .52, -.45),
        ('moon_moth', (.74, -.22, 1.36), .40, .75),
        ('lantern_snail', (.17, -1.27, 0), .72, -.45),
    ],
    'hex_butterfly_glade': [
        ('spiral_tree', (0, .45, 0), .97, -.12),
        ('lantern_flower', (-1.05, -.59, 0), 1.05, -.3),
        ('lantern_flower', (.90, -.63, 0), .82, .5),
        ('lantern_flower', (.29, -1.11, 0), .69, -.8),
        ('spiral_fern', (-.93, .53, 0), .62, .8),
        ('mushroom_purple', (1.10, .40, 0), .43, .2),
        ('boulder', (-.89, -.38, 0), .59, .5),
        ('butterfly_cyan', (-.72, -.27, 1.60), .65, -.4),
        ('butterfly_sunset', (.68, -.22, 2.02), .56, .35),
        ('butterfly_cyan', (.59, -.91, 1.02), .46, .65),
        ('butterfly_sunset', (-.48, -.89, .70), .42, -.8),
        ('moon_moth', (.07, .08, 2.84), .43, -.6),
    ],
    'hex_dream_menagerie': [
        ('mushroom_purple', (-.45, .61, 0), 1.22, .2),
        ('mushroom_blue', (.94, .65, 0), .67, .7),
        ('crystal_purple', (-1.23, .18, 0), .52, .2),
        ('boulder', (.83, -.25, 0), .73, .4),
        ('jackalope', (-.47, -.63, 0), .97, -.20),
        ('jackalope', (.27, .30, 0), .62, .15),
        ('lantern_snail', (.73, -1.08, 0), 1.10, -.55),
        ('lantern_flower', (-1.06, -.80, 0), .78, -.4),
        ('spiral_fern', (.0, -1.36, 0), .64, .4),
        ('spiral_fern', (1.17, -.18, 0), .69, -.9),
        ('butterfly_sunset', (-.21, -.19, 1.68), .53, -.45),
        ('butterfly_cyan', (.71, .44, 1.70), .43, .55),
    ],
}


def place(kind, pos, scale=1, rotation=0):
    library = dream if kind in dream.BUILDERS else forest
    return library.place(kind, pos, scale, (0, 0, rotation))


def contacts():
    # Uneven little islands of growth follow object contacts, leaving clear paths.
    vertices, faces = [], []
    for i, (x, y, scale) in enumerate([
            (-1.01, -.64, .73), (.93, -.49, .78), (-.52, .32, .65),
            (.45, .70, .74), (-1.21, .58, .55), (.19, -1.29, .50)]):
        forest.place('moss', (x, y, .006), (scale, scale * .83, .48), (0, 0, i * .89))
        for j in range(3):
            a = i * 1.73 + j * 2.1
            forest.place('leaf_clump', (x + .21 * math.cos(a), y + .17 * math.sin(a), 0),
                         (.73 + j * .10) * scale, (0, 0, a))
        for j in range(7):
            a = i * .89 + j * 2.399963
            bx, by = x + .30 * math.cos(a), y + .25 * math.sin(a)
            h = .09 + .06 * math.sin(j * 1.7 + i) ** 2
            n = len(vertices)
            vertices.extend([(bx - .013, by, .009), (bx + .013, by, .009),
                             (bx + .03 * math.cos(a), by + .03 * math.sin(a), h)])
            faces.append((n, n + 1, n + 2))
        if i % 2 == 0:
            forest.place('mushroom_small', (x + .22, y - .08, 0), .67, (0, 0, i))
    for i in range(4):
        angle = i * 1.7
        forest.place('fern', (1.13 * math.cos(angle), .94 * math.sin(angle), 0),
                     .39 + .08 * (i % 2), (0, 0, angle))
    grass = g.mesh('Fine grasses around dreaming forest contacts', vertices, faces, 'forest_leaf_light')
    uv = grass.data.uv_layers.new(name=style.TEXTURES.uv_name)
    for poly in grass.data.polygons:
        for index, coord in zip(poly.loop_indices, [(0, 0), (1, 0), (.5, 1)], strict=True):
            uv.data[index].uv = coord


def build_one(name, render=True):
    g.clear_scene()
    dream.reset()
    asset = g.collection(name)
    g.target(asset)
    root = g.empty(name + '_root')
    forest.place('hex_meadow')
    for kind, pos, scale, angle in RECIPES[name]:
        place(kind, pos, scale, angle)
    contacts()
    g.attach_all(asset, root)
    root['asset_role'] = name
    root['hex_radius'] = style.HEX.radius
    root['hex_orientation'] = 'flat_top'
    root['grid_spacing_x'] = style.HEX.spacing_x
    root['grid_spacing_y'] = style.HEX.spacing_y
    root['ground_origin'] = 'meadow surface z=0; foundation bottom from art_style.HEX'
    root['river_connections'] = ''
    root['modeling_stage'] = paint.VERSION
    asset.asset_mark()
    asset.asset_data.description = 'Complete dreaming forest hex: ' + name.replace('hex_', '').replace('_', ' ')
    paint.apply(asset)
    paint.ground(asset, name)
    g.studio(1.20, 6.65)
    scene = bpy.context.scene
    scene.name = name
    scene.render.filepath = str(g.ROOT / 'exports/previews' / (name + '.png'))
    bpy.ops.wm.save_as_mainfile(filepath=str(g.ROOT / 'sources/environment' / (name + '.blend')))
    if render:
        bpy.ops.render.render(write_still=True)
    print('Saved dreaming forest tile:', name, flush=True)


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    for name in [a for a in args if a != '--no-render'] or list(RECIPES):
        build_one(name, '--no-render' not in args)
