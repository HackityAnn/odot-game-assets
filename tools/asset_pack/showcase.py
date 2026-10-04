"""Assemble editable asset collections into a single overview Blender file."""
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
from mathutils import Vector
import geometry as g
from catalog import BY_ID, EVIL


def main():
    g.clear_scene()
    autobattler='--autobattler' in sys.argv
    evil='--evil' in sys.argv
    names=['arrow_tower','bombarding_tower','barracks','magic_academy',
           'stone_cutter','tavern','trade_market','berserker']
    slots=[(name,BY_ID[name]['category'],((i%2-.5)*6,2.8 if i<2 else -2.8,0)) for i,name in enumerate(EVIL)] if evil else [(name,BY_ID[name]['category'],((i%4-1.5)*6,3 if i<4 else -4,0)) for i,name in enumerate(names)] if autobattler else [
           ('tree_house','buildings',(-9,3,0)),('bakery','buildings',(-3,3,0)),
           ('gold_mine','buildings',(3,3,0)),('woodcutter_hut','buildings',(9,3,0)),
           ('knight','characters',(-6,-4,0)),('mage','characters',(0,-4,0)),('archer','characters',(6,-4,0))]
    for name,category,pos in slots:
        path=g.ROOT/'sources'/category/f'{name}.blend'
        with bpy.data.libraries.load(str(path),link=False) as (source,dest):
            dest.collections=[c for c in source.collections if c==name or c.startswith('DISPLAY_') or c=='EQUIPMENT']
        imported=[c for c in dest.collections if c]
        for col in imported: bpy.context.scene.collection.children.link(col)
        main_col=next(c for c in imported if c.name==name)
        main_col.asset_mark(); main_col.asset_data.description='Original reconstruction from the supplied '+BY_ID[name]['title']+' reference.'
        stage=g.collection(name+'_display'); g.target(stage)
        root=g.empty(name+'_display_root',pos)
        for col in imported:
            for obj in col.objects:
                if obj.parent is None: obj.parent=root
        rig=next((o for col in imported for o in col.objects if o.type=='ARMATURE'),None)
        if rig:
            # Retain the authored idle stance, including costume-specific arm poses.
            rig['overview_pose']='idle at frame 1; individual sources retain all six clips'
    studio=g.studio(1.6,16 if evil else 28)
    scene=bpy.context.scene; scene.name='Evil units — initial reference models' if evil else 'Autobattler — new reference asset set' if autobattler else 'Fantasy village — reference asset set'
    scene.frame_set(1)
    scene.camera.location=(7,-15,14) if evil else (10,-22,19)
    scene.camera.rotation_euler=(Vector((0,0,1.7))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    for light in [o for o in studio.objects if o.type=='LIGHT']:
        light.location*=3; light.data.energy*=9; light.data.size*=3
        light.rotation_euler=(Vector((0,0,1.5))-light.location).to_track_quat('-Z','Y').to_euler()
    reference=bpy.data.images.load(str(g.ROOT/'sources'/'reference'/'fantasy_village.png'),check_existing=True)
    reference.pack(); reference.use_fake_user=True
    if autobattler or evil:
        for name in EVIL if evil else names:
            image=bpy.data.images.load(str(g.ROOT/'sources/reference'/BY_ID[name]['reference']),check_existing=True)
            image.pack(); image.use_fake_user=True
    text=bpy.data.texts.new('START HERE')
    text.write(('Four initial evil unit models based on the new supplied references.\n' if evil else 'Eight new models based on the individual autobattler references.\n' if autobattler else 'Seven original models based on the supplied reference.\n')+
               'Each building and character has its own editable source file.\n'
               'DISPLAY_TERRAIN and DISPLAY_ATMOSPHERE are separate presentation collections.\n'
               'Character clips: idle, walk, run, attack, hit, death.\n'
               'Equipment grips are centered at each prop root.\n'
               'No meshes or animation conventions were taken from the existing game.\n'
               'Supplied references are packed into Images.\n'
               'Repeated props share meshes from sources/props/shared_village_kit.blend.\n')
    scene.render.resolution_x=1800; scene.render.resolution_y=1200
    scene.render.filepath=str(g.ROOT/'exports'/'previews'/('evil_overview.png' if evil else 'autobattler_overview.png' if autobattler else 'overview.png'))
    bpy.ops.wm.save_as_mainfile(filepath=str(g.ROOT/'sources'/('evil_autobattler.blend' if evil else 'autobattler.blend' if autobattler else 'fantasy_village.blend')))
    bpy.ops.render.render(write_still=True)


if __name__=='__main__': main()
