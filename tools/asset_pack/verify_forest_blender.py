"""Check authored forest tiles for grid fit, component reuse, and library freshness.

Read-only worker: opens sources and compares embedded meshes to library prototypes.
"""
import hashlib
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import forest_kit as kit
from forest_tiles import RECIPES
from enchanted_tiles import RECIPES as DREAM_RECIPES
import geometry as g
import art_style as style


def geometry_signature(obj):
    values=(tuple(tuple(round(c,6) for c in vertex.co) for vertex in obj.data.vertices),
            tuple(tuple(poly.vertices) for poly in obj.data.polygons))
    return hashlib.sha256(repr(values).encode()).hexdigest()


def main(names=None):
    recipes = RECIPES | DREAM_RECIPES
    for name in names or recipes:
        path=g.ROOT/'sources/environment'/f'{name}.blend'
        bpy.ops.wm.open_mainfile(filepath=str(path))
        asset=bpy.data.collections[name];root=bpy.data.objects[name+'_root']
        assert root.location.length<1e-6,(name,'tile origin')
        assert root['hex_radius']==kit.RADIUS,(name,'grid radius')
        assert root['grid_spacing_x']==1.5*kit.RADIUS,(name,'horizontal grid spacing')
        assert abs(root['grid_spacing_y']-2*kit.HEIGHT)<1e-6,(name,'vertical grid spacing')
        bpy.context.view_layer.update()
        points=[obj.matrix_world @ vertex.co for obj in asset.objects if obj.type=='MESH' for vertex in obj.data.vertices]
        assert abs(min(p.z for p in points)-style.HEX.bottom)<style.GEOMETRY.pivot_tolerance,(name,'foundation height')
        for p in points:
            assert style.HEX.contains(p.x,p.y,style.GEOMETRY.footprint_tolerance),(name,'outside hex edge',tuple(p))
        instances=[obj for obj in asset.objects if obj.get('kit_asset') and obj.get('kit_source')]
        for library in sorted({obj['kit_source'] for obj in instances}):
            group=[obj for obj in instances if obj['kit_source']==library]
            kinds=sorted({obj['kit_asset'] for obj in group})
            with bpy.data.libraries.load(str(g.ROOT/library),link=False) as (_,dest):dest.collections=list(kinds)
            prototypes={kind:col for kind,col in zip(kinds,dest.collections,strict=True)}
            for instance in group:
                signatures=sorted(geometry_signature(o) for o in instance.children if o.type=='MESH')
                expected=sorted(geometry_signature(o) for o in prototypes[instance['kit_asset']].objects if o.type=='MESH')
                assert signatures==expected,(name,instance.name,'stale embedded library geometry')
        base=next(o for o in instances if o['kit_asset'] in ['forest_hex_meadow','forest_hex_stream'])
        # The base cannot rotate, scale or shift the common tile footprint.
        assert base.matrix_world==root.matrix_world,(name,'base placement')
        if root['river_connections']:
            assert base['kit_asset']=='forest_hex_stream',(name,'river channel base')
            # Both river endpoints have the same height and width for tile seams.
            water=next(o for o in base.children if o.name.startswith('Continuous river water'))
            vertices=[o.co for o in water.data.vertices]
            assert abs(max(p.y for p in vertices)-kit.HEIGHT)<1e-6
            assert abs(min(p.y for p in vertices)+kit.HEIGHT)<1e-6
        print('Verified grid fit and fresh library geometry:',name,flush=True)
    print('Verified forest tiles:',len(names or recipes))


if __name__=='__main__':main(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
