"""Round-trip validation: geometry, materials, rig playback, and attached equipment."""
import json
import argparse
import hashlib
import math
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import bpy
import geometry as g
from export_pack import BUILDINGS,CHARACTERS,CLIPS
from tools.asset_catalog.export_sources import plan_exports
from tools.asset_catalog.blender_selection import load_asset
from tools.asset_catalog.index import write_json


def snapshot(objects):
    bpy.context.view_layer.update()
    depsgraph=bpy.context.evaluated_depsgraph_get()
    points=[]
    for obj in objects:
        if obj.type!='MESH' or obj.hide_render or all(col.hide_render for col in obj.users_collection): continue
        evaluated=obj.evaluated_get(depsgraph)
        mesh=evaluated.to_mesh()
        points.extend(tuple(evaluated.matrix_world @ vertex.co) for vertex in mesh.vertices)
        evaluated.to_mesh_clear()
    assert points
    assert all(math.isfinite(c) for p in points for c in p)
    return {'min':[min(p[i] for p in points) for i in range(3)],
            'max':[max(p[i] for p in points) for i in range(3)]}


def main(root=g.ROOT, assets=None):
    root=Path(root).resolve()
    jobs=plan_exports(root, assets)
    results=[]
    for job in jobs:
        asset_id=job['id']; name=Path(asset_id).name
        category=Path(asset_id).parts[0]
        objects=load_asset(job, root)
        animated=any(obj.type=='ARMATURE' for obj in objects)
        instances=[obj for obj in objects if obj.get('kit_asset')]
        reuse={}
        for instance in instances:
            reuse[instance['kit_asset']]=reuse.get(instance['kit_asset'],0)+1
        # Repeated kit parts must share mesh datablocks in the editable source.
        for kind,count in reuse.items():
            parts=[obj for instance in instances if instance['kit_asset']==kind for obj in instance.children if obj.type=='MESH']
            if count>1:
                assert len({obj.data.as_pointer() for obj in parts})<len(parts),(name,kind,'geometry was copied instead of reused')
        before=snapshot(objects)
        source_clip_bounds={}
        if animated:
            source_rig=next(obj for obj in objects if obj.type=='ARMATURE')
            for clip in sorted(CLIPS):
                source_rig.animation_data.action=bpy.data.actions[clip]
                start,end=source_rig.animation_data.action.frame_range
                frames=[int(round(frame)) for frame in [start,start+(end-start)/4,(start+end)/2,end]]
                source_clip_bounds[clip]=[]
                for frame in frames:
                    bpy.context.scene.frame_set(frame)
                    source_clip_bounds[clip].append(snapshot(objects))
        for obj in list(bpy.data.objects): bpy.data.objects.remove(obj,do_unlink=True)
        for action in list(bpy.data.actions): bpy.data.actions.remove(action)
        bpy.ops.import_scene.gltf(filepath=str(root/'exports'/f'{asset_id}.glb'))
        bpy.context.scene.frame_set(1)
        # Blender's importer adds a hidden, unmaterialed joint-display icosphere.
        imported=[o for o in bpy.context.scene.objects
                  if o.type!='MESH' or not all(col.hide_render for col in o.users_collection)]
        after=snapshot(imported)
        error=max(abs(before[key][i]-after[key][i]) for key in ['min','max'] for i in range(3))
        assert error<.005,(name,'round-trip bounds changed',before,after)
        # Boulders and tree roots intentionally extend into the ground; the root stays at zero.
        if name in BUILDINGS+CHARACTERS:
            imported_root=bpy.data.objects.get(name+'_root')
            assert imported_root and imported_root.location.length<.005,(name,'root pivot')
            assert after['min'][2]>(-.35 if category=='buildings' else -.05),(name,'excessive ground penetration',after)
        assert all(o.data.materials for o in imported if o.type=='MESH'),(name,'missing material')
        report={'asset':name if name in BUILDINGS+CHARACTERS else asset_id,
                'asset_id':asset_id,'round_trip_max_bounds_error':round(error,6),'geometry_finite':True}
        report['source_sha256']=hashlib.sha256((root/job['source']).read_bytes()).hexdigest()
        report['glb_sha256']=hashlib.sha256((root/'exports'/f'{asset_id}.glb').read_bytes()).hexdigest()
        if reuse: report['shared_kit_instances']=reuse
        if animated:
            rig=next(o for o in imported if o.type=='ARMATURE')
            assert len(rig.data.bones)==19,(name,'bone count')
            assert set(a.name for a in bpy.data.actions)==CLIPS,(name,[a.name for a in bpy.data.actions])
            assert any(o.type=='MESH' and o.vertex_groups for o in imported),(name,'skin weights')
            assert all(o.data.materials for o in imported if o.type=='MESH'),(name,'missing material')
            samples={}
            for clip in sorted(CLIPS):
                rig.animation_data.action=bpy.data.actions[clip]
                snapshots=[]
                start,end=rig.animation_data.action.frame_range
                for frame in [start,start+(end-start)/4,(start+end)/2,end]:
                    bpy.context.scene.frame_set(int(round(frame)))
                    snapshots.append(snapshot(imported))
                if clip in ['walk','run','attack','death']:
                    assert any(snapshots[0]!=sample for sample in snapshots[1:-1]),(name,clip,'no deformation')
                if clip in ['idle','walk','run']:
                    delta=max(abs(snapshots[0][k][i]-snapshots[-1][k][i]) for k in ['min','max'] for i in range(3))
                    assert delta<.005,(name,clip,'loop discontinuity',delta)
                pose_error=max(abs(source[key][i]-imported_pose[key][i])
                               for source,imported_pose in zip(source_clip_bounds[clip],snapshots)
                               for key in ['min','max'] for i in range(3))
                assert pose_error<.005,(name,clip,'animated export differs from source',pose_error)
                samples[clip]='finite geometry; playback checked'
            report['clips']=samples
        results.append(report)
        print(f'Verified {asset_id}',flush=True)
    path=root/'exports/validation.json'
    previous=json.loads(path.read_text()) if path.exists() else []
    records={entry['asset']:entry for entry in previous}
    records.update({entry['asset']:entry for entry in results})
    write_json(path,list(records.values()))
    print(f'Verified {len(results)} assets; retained {len(records)-len(results)} other results')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('assets',nargs='*',help='Canonical IDs, e.g. characters/berserker')
    parser.add_argument('--all',action='store_true',help='Include standalone props and terrain')
    parser.add_argument('--root',type=Path,default=g.ROOT)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    selected=args.assets or (None if args.all else
             ['buildings/'+name for name in BUILDINGS]+['characters/'+name for name in CHARACTERS])
    main(args.root,selected)
