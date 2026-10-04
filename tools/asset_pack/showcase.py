"""Assemble editable asset collections into a single overview Blender file."""
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
from mathutils import Vector
import geometry as g


def main():
    g.clear_scene()
    slots=[('tree_house','buildings',(-9,3,0)),('bakery','buildings',(-3,3,0)),
           ('gold_mine','buildings',(3,3,0)),('woodcutter_hut','buildings',(9,3,0)),
           ('knight','characters',(-6,-4,0)),('mage','characters',(0,-4,0)),('archer','characters',(6,-4,0))]
    for name,category,pos in slots:
        path=g.ROOT/'sources'/category/f'{name}.blend'
        with bpy.data.libraries.load(str(path),link=False) as (source,dest):
            dest.collections=[c for c in source.collections if c==name or c.startswith('DISPLAY_') or c=='EQUIPMENT']
        imported=[c for c in dest.collections if c]
        for col in imported: bpy.context.scene.collection.children.link(col)
        main_col=next(c for c in imported if c.name==name)
        main_col.asset_mark(); main_col.asset_data.description='Original reconstruction from the supplied fantasy village reference.'
        stage=g.collection(name+'_display'); g.target(stage)
        root=g.empty(name+'_display_root',pos)
        for col in imported:
            for obj in col.objects:
                if obj.parent is None: obj.parent=root
        rig=next((o for col in imported for o in col.objects if o.type=='ARMATURE'),None)
        if rig:
            # Overview is intentionally held in the rest pose; individual sources keep their clips.
            rig.animation_data.action=None
            for bone in rig.pose.bones: bone.matrix_basis.identity()
    studio=g.studio(1.6,28)
    scene=bpy.context.scene; scene.name='Fantasy village — reference asset set'
    scene.camera.location=(10,-22,19)
    scene.camera.rotation_euler=(Vector((0,0,1.7))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    for light in [o for o in studio.objects if o.type=='LIGHT']:
        light.location*=3; light.data.energy*=9; light.data.size*=3
        light.rotation_euler=(Vector((0,0,1.5))-light.location).to_track_quat('-Z','Y').to_euler()
    reference=bpy.data.images.load(str(g.ROOT/'sources'/'reference'/'fantasy_village.png'),check_existing=True)
    reference.pack(); reference.use_fake_user=True
    text=bpy.data.texts.new('START HERE')
    text.write('Seven original models based on the supplied reference.\n'
               'Each building and character has its own editable source file.\n'
               'DISPLAY_TERRAIN and DISPLAY_ATMOSPHERE are separate presentation collections.\n'
               'Character clips: idle, walk, run, attack, hit, death.\n'
               'Equipment grips are centered at each prop root.\n'
               'No meshes or animation conventions were taken from the existing game.\n'
               'The supplied reference is packed into Images: fantasy_village.png.\n')
    scene.render.resolution_x=1800; scene.render.resolution_y=1200
    scene.render.filepath=str(g.ROOT/'exports'/'previews'/'overview.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(g.ROOT/'sources'/'fantasy_village.blend'))
    bpy.ops.render.render(write_still=True)


if __name__=='__main__': main()
