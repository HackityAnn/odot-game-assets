"""Round-trip validation: geometry, materials, rig playback, and attached equipment."""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import geometry as g
from export_pack import BUILDINGS,CHARACTERS,CLIPS,inspect_glb


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


def main():
    results=[]
    for name in BUILDINGS+CHARACTERS:
        category='characters' if name in CHARACTERS else 'buildings'
        bpy.ops.wm.open_mainfile(filepath=str(g.ROOT/'sources'/category/f'{name}.blend'))
        bpy.context.scene.frame_set(1)
        objects=list(bpy.data.collections[name].objects)
        if name in CHARACTERS: objects+=list(bpy.data.collections['EQUIPMENT'].objects)
        before=snapshot(objects)
        for obj in list(bpy.data.objects): bpy.data.objects.remove(obj,do_unlink=True)
        for action in list(bpy.data.actions): bpy.data.actions.remove(action)
        bpy.ops.import_scene.gltf(filepath=str(g.ROOT/'exports'/category/f'{name}.glb'))
        bpy.context.scene.frame_set(1)
        # Blender's importer adds a hidden, unmaterialed joint-display icosphere.
        imported=[o for o in bpy.context.scene.objects
                  if o.type!='MESH' or not all(col.hide_render for col in o.users_collection)]
        after=snapshot(imported)
        error=max(abs(before[key][i]-after[key][i]) for key in ['min','max'] for i in range(3))
        assert error<.005,(name,'round-trip bounds changed',before,after)
        # Boulders and tree roots intentionally extend into the ground; the root stays at zero.
        imported_root=bpy.data.objects.get(name+'_root')
        assert imported_root and imported_root.location.length<.005,(name,'root pivot')
        assert after['min'][2]>(-.35 if category=='buildings' else -.05),(name,'excessive ground penetration',after)
        report={'asset':name,'round_trip_max_bounds_error':round(error,6),'geometry_finite':True}
        if name in CHARACTERS:
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
                samples[clip]='finite geometry; playback checked'
            report['clips']=samples
        results.append(report)
    (g.ROOT/'exports'/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))


if __name__=='__main__': main()
