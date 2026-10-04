"""Run with Blender's Python, or import into an agent-owned Blender instance."""
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import geometry as g
import buildings
import characters


def build_one(name, render=True):
    g.clear_scene()
    scene=bpy.context.scene
    scene.name=name
    asset=g.collection(name); g.target(asset)
    root=g.empty(name+'_root')
    root['asset_role']=name; root['forward']='-Y'; root['ground_origin']='z=0'
    is_character=name in ['knight','mage','archer']
    props=None
    if is_character:
        props=g.collection('EQUIPMENT')
        characters.build(name,asset,props)
    else:
        buildings.BUILDERS[name]()
    g.attach_all(asset,root)
    terrain=g.collection('DISPLAY_TERRAIN'); g.target(terrain); g.terrain(1.85 if is_character else 2.55)
    # Trees are display dressing, deliberately separate from the building export.
    if name!='tree_house' and not is_character:
        g.pine((-1.39,1.17,0),2.8); g.pine((1.40,1.30,0),2.1)
        if name=='gold_mine': g.pine((.03,1.74,0),3.5)
    if name in ['bakery','woodcutter_hut']:
        atmosphere=g.collection('DISPLAY_ATMOSPHERE'); g.target(atmosphere); g.chimney_smoke()
    if is_character:
        if name=='mage': g.mushroom((1.1,-.35,0),.46)
        g.stepping_stone((.2,-1.02),.24); g.stepping_stone((.70,-1.10),.22)
    g.studio(1.4 if is_character else 2.1 if name=='tree_house' else 2.05 if name in ['bakery','woodcutter_hut'] else 1.80,
             4.35 if is_character else 6.3 if name=='tree_house' else 6.4 if name in ['bakery','woodcutter_hut'] else 5.9)
    category='characters' if is_character else 'buildings'
    path=g.ROOT/'sources'/category/f'{name}.blend'
    scene.render.filepath=str(g.ROOT/'exports'/'previews'/f'{name}.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    if render:
        if name=='archer':
            rig=next(o for o in asset.objects if o.type=='ARMATURE')
            rig.animation_data.action=bpy.data.actions['attack']
            scene.frame_set(13)
        bpy.ops.render.render(write_still=True)
    print(json.dumps({'asset':name,'blend':str(path),'objects':len(asset.objects),'preview':scene.render.filepath}))


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['woodcutter_hut']
    render='--no-render' not in args
    for name in [arg for arg in args if arg!='--no-render']: build_one(name,render=render)
