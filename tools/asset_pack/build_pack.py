"""Run with Blender's Python, or import into an agent-owned Blender instance."""
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import geometry as g
import buildings
import characters
import catalog
import village_kit as kit
import autobattler_buildings
import berserker
import evil_units


def build_one(name, render=True):
    g.clear_scene()
    kit.reset()
    scene=bpy.context.scene
    scene.name=name
    asset=g.collection(name); g.target(asset)
    root=g.empty(name+'_root')
    root['asset_role']=name; root['forward']='-Y'; root['ground_origin']='z=0'
    is_character=name in catalog.CHARACTERS
    props=None
    if is_character:
        props=g.collection('EQUIPMENT')
        if name in catalog.EVIL: evil_units.build(name,asset,props)
        elif name=='berserker': berserker.build(asset,props)
        else: characters.build(name,asset,props)
    else:
        builder=autobattler_buildings.BUILDERS.get(name) or buildings.BUILDERS[name]
        builder()
    g.attach_all(asset,root)
    terrain=g.collection('DISPLAY_TERRAIN'); g.target(terrain); g.terrain(1.85 if is_character else 2.55)
    # Trees are display dressing, deliberately separate from the building export.
    if name!='tree_house' and not is_character:
        if name in catalog.NEW:
            if name in ['barracks','magic_academy']: kit.place('pine',(-1.39,1.17,0),1.10)
            if name in ['tavern','magic_academy']: kit.place('pine',(1.40,1.30,0),.92)
            if name=='stone_cutter':
                g.lathe('Workshop leafy tree trunk',[(0,.13),(1.8,.075)],'bark',8,(1.36,1.28,0))
                for pos,scale in [((1.36,1.28,1.65),1.7),((1.28,1.23,1.14),1.25)]: kit.place('shrub',pos,scale)
        else:
            g.pine((-1.39,1.17,0),2.8); g.pine((1.40,1.30,0),2.1)
            if name=='gold_mine': g.pine((.03,1.74,0),3.5)
    if name in ['bakery','woodcutter_hut','tavern','stone_cutter']:
        atmosphere=g.collection('DISPLAY_ATMOSPHERE'); g.target(atmosphere); g.chimney_smoke()
    if is_character:
        if name=='mage': g.mushroom((1.1,-.35,0),.46)
        g.stepping_stone((.2,-1.02),.24); g.stepping_stone((.70,-1.10),.22)
        if name in ['evil_mage_unit','evil_berserker_unit']: kit.place('skull',(-1.02,-.45,.01),.37,(0,0,-.2))
    if name in catalog.NEW:
        g.studio(1.47 if is_character else 2.55 if name=='magic_academy' else 2.26 if name=='arrow_tower' else 2.05,
                 4.8 if name=='evil_mage_unit' else 4.5 if is_character else 7.2 if name=='magic_academy' else 6.9 if name=='arrow_tower' else 6.6)
    else:
        g.studio(1.4 if is_character else 2.1 if name=='tree_house' else 2.05 if name in ['bakery','woodcutter_hut'] else 1.80,
                 4.35 if is_character else 6.3 if name=='tree_house' else 6.4 if name in ['bakery','woodcutter_hut'] else 5.9)
    category='characters' if is_character else 'buildings'
    path=g.ROOT/'sources'/category/f'{name}.blend'
    scene.render.filepath=str(g.ROOT/'exports'/'previews'/f'{name}.png')
    if name in catalog.NEW:
        reference=bpy.data.images.load(str(g.ROOT/'sources/reference'/catalog.BY_ID[name]['reference']),check_existing=True)
        reference.pack(); reference.use_fake_user=True
        root['reference']='sources/reference/'+catalog.BY_ID[name]['reference']
        root['modeling_stage']='initial_model' if name in catalog.EVIL else 'modeled_for_review'
        asset.asset_mark(); asset.asset_data.description='Modeled from '+catalog.BY_ID[name]['title']+' reference; visual review precedes optimization.'
    if not is_character:
        root['modeling_stage']='upgraded_reference_pass'
        root['art_direction']='Bold role emblems, substantial timbers, projecting joinery, layered roofs and recessed portals.'
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
