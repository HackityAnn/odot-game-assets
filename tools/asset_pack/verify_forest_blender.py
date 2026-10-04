"""Check authored forest tiles for grid fit, component reuse, and library freshness.

Read-only worker: opens sources and compares embedded meshes to library prototypes.
"""
import hashlib
import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import forest_kit as kit
from forest_tiles import RECIPES
import geometry as g


def geometry_signature(obj):
    values=(tuple(tuple(round(c,6) for c in vertex.co) for vertex in obj.data.vertices),
            tuple(tuple(poly.vertices) for poly in obj.data.polygons))
    return hashlib.sha256(repr(values).encode()).hexdigest()


def main():
    for name in RECIPES:
        path=g.ROOT/'sources/environment'/f'{name}.blend'
        bpy.ops.wm.open_mainfile(filepath=str(path))
        asset=bpy.data.collections[name];root=bpy.data.objects[name+'_root']
        assert root.location.length<1e-6,(name,'tile origin')
        assert root['hex_radius']==kit.RADIUS,(name,'grid radius')
        assert root['grid_spacing_x']==1.5*kit.RADIUS,(name,'horizontal grid spacing')
        assert abs(root['grid_spacing_y']-2*kit.HEIGHT)<1e-6,(name,'vertical grid spacing')
        bpy.context.view_layer.update()
        points=[obj.matrix_world @ vertex.co for obj in asset.objects if obj.type=='MESH' for vertex in obj.data.vertices]
        assert abs(min(p.z for p in points)+.36)<1e-6,(name,'foundation height')
        for p in points:
            assert abs(p.y)<=kit.HEIGHT+.025,(name,'outside hex Y edge',tuple(p))
            assert math.sqrt(3)*abs(p.x)+abs(p.y)<=math.sqrt(3)*kit.RADIUS+.025,(name,'outside hex diagonal',tuple(p))
        instances=[obj for obj in asset.objects if obj.get('kit_asset') and
                   obj.get('kit_source')=='sources/environment/shared_forest_kit.blend']
        kinds=sorted({obj['kit_asset'] for obj in instances})
        with bpy.data.libraries.load(str(kit.LIBRARY),link=False) as (_,dest):dest.collections=list(kinds)
        prototypes={kind:col for kind,col in zip(kinds,dest.collections,strict=True)}
        for instance in instances:
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
    print('Verified all eight forest tiles')


if __name__=='__main__':main()
