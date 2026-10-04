"""Export portable assets and verify the binary glTF structure."""
import json
import math
import struct
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
from mathutils import Matrix
import geometry as g

BUILDINGS=['woodcutter_hut','bakery','gold_mine','tree_house']
CHARACTERS=['knight','mage','archer']
CLIPS={'idle','walk','run','attack','hit','death'}


def export(path,objects,animated=False):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects: obj.hide_set(False); obj.select_set(True)
    bpy.context.view_layer.objects.active=next((o for o in objects if o.type=='ARMATURE'),objects[0])
    options=dict(filepath=str(path),use_selection=True,export_animations=animated,
                 export_apply=True,export_extras=True,export_cameras=False,export_lights=False,
                 export_yup=True,export_skins=animated,export_animation_mode='ACTIONS')
    # The current exporter defaults to GLB; its format enum is dynamically populated.
    result=bpy.ops.export_scene.gltf(**options)
    if 'FINISHED' not in result or not path.exists(): raise RuntimeError(f'Export failed: {path}')


def write_source(path,objects,name):
    # Save an isolated scene in the worker. The source file on disk stays untouched.
    keep={obj.name for obj in objects}
    for obj in list(bpy.data.objects):
        if obj.name not in keep: bpy.data.objects.remove(obj,do_unlink=True)
    bpy.context.scene.name=name
    bpy.context.scene.camera=None
    bpy.ops.wm.save_as_mainfile(filepath=str(path),copy=True)


def inspect_glb(path):
    raw=path.read_bytes()
    magic,version,length=struct.unpack_from('<4sII',raw)
    assert magic==b'glTF' and version==2 and length==len(raw),path
    chunk_length,kind=struct.unpack_from('<I4s',raw,12)
    assert kind==b'JSON',path
    data=json.loads(raw[20:20+chunk_length])
    assert data.get('meshes') and data.get('materials'),path
    assert not data.get('cameras'),path
    assert all(not buffer.get('uri') for buffer in data.get('buffers',[])),path
    triangles=0
    for mesh in data['meshes']:
        for primitive in mesh['primitives']:
            assert primitive.get('mode',4)==4,path
            count=data['accessors'][primitive['indices']]['count'] if 'indices' in primitive else data['accessors'][primitive['attributes']['POSITION']]['count']
            triangles+=count//3
    animations=[a['name'] for a in data.get('animations',[])]
    return dict(file=str(path.relative_to(g.ROOT)),bytes=len(raw),meshes=len(data['meshes']),
                triangles=triangles,materials=len(data['materials']),animations=animations,
                skins=len(data.get('skins',[])))


def main():
    reports=[]
    source_jobs=[]
    for name in BUILDINGS+CHARACTERS:
        animated=name in CHARACTERS; category='characters' if animated else 'buildings'
        source=g.ROOT/'sources'/category/f'{name}.blend'
        bpy.ops.wm.open_mainfile(filepath=str(source))
        scene=bpy.context.scene; scene.frame_set(1)
        objects=list(bpy.data.collections[name].objects)
        equipment=bpy.data.collections.get('EQUIPMENT')
        if equipment: objects+=list(equipment.objects)
        path=g.ROOT/'exports'/category/f'{name}.glb'
        export(path,objects,animated)
        report=inspect_glb(path)
        if animated:
            assert set(report['animations'])==CLIPS,(name,report['animations'])
            assert report['skins']>0,name
            rig=next(o for o in objects if o.type=='ARMATURE')
            assert len(rig.data.bones)==19,name
            report['bones']=19
        else: assert not report['animations'] and not report['skins'],name
        reports.append(report)
        if name in ['woodcutter_hut','knight']:
            tile='hex_meadow_building' if name=='woodcutter_hut' else 'hex_meadow_character'
            terrain=list(bpy.data.collections['DISPLAY_TERRAIN'].objects)
            export(g.ROOT/'exports'/'environment'/f'{tile}.glb',terrain)
            source_jobs.append((source,'environment',tile,'DISPLAY_TERRAIN',None))
            reports.append(inspect_glb(g.ROOT/'exports'/'environment'/f'{tile}.glb'))
        if equipment:
            for root in [o for o in equipment.objects if o.type=='EMPTY']:
                prop_name=root.name
                prop_objects=[root]+list(root.children_recursive)
                root.parent=None; root.matrix_world=Matrix.Identity(4)
                export(g.ROOT/'exports'/'props'/f'{prop_name}.glb',prop_objects)
                source_jobs.append((source,'props',prop_name,'EQUIPMENT',prop_name))
                reports.append(inspect_glb(g.ROOT/'exports'/'props'/f'{prop_name}.glb'))
    for source,category,name,col_name,root_name in source_jobs:
        bpy.ops.wm.open_mainfile(filepath=str(source))
        if root_name:
            root=bpy.data.objects[root_name]
            objects=[root]+list(root.children_recursive)
            root.parent=None; root.matrix_world=Matrix.Identity(4)
        else:
            objects=list(bpy.data.collections[col_name].objects)
        write_source(g.ROOT/'sources'/category/f'{name}.blend',objects,name)
    manifest={'reference':'sources/reference/fantasy_village.png',
              'blender':bpy.app.version_string,'art_direction':'supplied reference; independent of existing game',
              'coordinates':{'source_up':'+Z','source_forward':'-Y','export_up':'+Y','export_forward':'+Z','ground':0},
              'animation_fps':24,'looping_clips':['idle','walk','run'],
              'one_shot_clips':['attack','hit','death'],
              'assets':reports}
    (g.ROOT/'exports'/'asset_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__': main()
