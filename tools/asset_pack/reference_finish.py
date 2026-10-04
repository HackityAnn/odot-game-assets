"""Reference palette, selective edge treatment and soft presentation lighting."""
import math
import re
import bpy
import geometry as g
import art_style as style
import style_blender


def palette():
    for name, spec in style.PAINTED_MATERIALS.items():
        g.material(name, spec.color, spec.roughness, spec.metallic, spec.emission)
    # Libraries append materials with numerical suffixes. Apply the same finish
    # to their actual material datablocks, retaining mesh/object slot sharing.
    for mat in list(bpy.data.materials):
        base=re.sub(r'\.\d+$','',mat.name)
        if base not in g.M or mat==g.M[base] or not mat.use_nodes:continue
        source=g.M[base]
        shader=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        original=next(n for n in source.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        if shader:
            for field in ['Base Color','Roughness','Metallic','Emission Color','Emission Strength']:
                shader.inputs[field].default_value=original.inputs[field].default_value
            mat.diffuse_color=source.diffuse_color


def rock_finish(obj):
    """Catch light on small edges; material maps supply the delicate fractures."""
    style_blender.stone_edges(obj)


def building_finish(name):
    palette()
    # Fine grain, pegs and tile seams follow baked geometry in each kit instance.
    for obj in list(g.CURRENT.objects):
        if obj.type!='MESH':continue
        base=obj.name.split('.')[0]
        if base.startswith(('Corner upright','Lookout upright','Mine entrance timber',
                            'Ore hoist upright','Canopy upright','Bell tower post')):
            verts=[v.co for v in obj.data.vertices]
            x0,x1=min(v.x for v in verts),max(v.x for v in verts)
            y=min(v.y for v in verts)-.009;z0,z1=min(v.z for v in verts),max(v.z for v in verts)
            if z1-z0<.4:continue
            for t in [-.22,.22]:
                x=(x0+x1)/2+(x1-x0)*t
                line=g.tube('Fine carved timber grain',[(x,y,z0+.10),(x+.009,y,(z0+z1)/2),(x-.006,y,z1-.10)],.005,'wood_dark',4)
                line.parent=obj.parent
            for z in [z0+.14,z1-.14]:
                peg=g.tube('Dark inset timber peg',[((x0+x1)/2,y,z),((x0+x1)/2,y-.013,z)],.021,'wood_dark',8)
                peg.parent=obj.parent
        if base=='Soft edged blue roof tile':
            seam=g.beam('Dark roof overlap seam',(-.17,-.147,.038),(.17,-.147,.038),.010,.013,'roof_blue_dark',.003)
            seam.parent=obj.parent
            ridge=g.beam('Shingle reflected edge',(-.17,.15,.039),(.17,.15,.039),.008,.012,'roof_blue_light',.002)
            ridge.parent=obj.parent
        if base=='Warm arched window':
            pts=[v.co for v in obj.data.vertices]
            x=(min(v.x for v in pts)+max(v.x for v in pts))/2;y=pts[0].y-.003
            z=min(v.z for v in pts);w=max(v.x for v in pts)-min(v.x for v in pts);h=max(v.z for v in pts)-z
            for row in range(2):
                patch=g.cube('Window golden intensity pane',(x-w*.23,y,z+h*(.22+.25*row)),(w*.36,.01,h*.19),'window_hot',.009)
                patch.parent=obj.parent
            shade=g.cube('Window lower amber shade',(x+w*.23,y,z+h*.22),(w*.36,.01,h*.20),'window_shade',.008)
            shade.parent=obj.parent
    for obj in list(g.CURRENT.objects):
        if obj.type=='MESH' and obj.name.startswith('Angular mine outcrop'):rock_finish(obj)
    # Readable metal corner straps and a little carved texture on ground steps.
    for obj in list(g.CURRENT.objects):
        if obj.type=='MESH' and obj.name.startswith('Limestone entrance step'):
            vs=[v.co for v in obj.data.vertices];z=max(v.z for v in vs)+.002
            x=(min(v.x for v in vs)+max(v.x for v in vs))/2;y=(min(v.y for v in vs)+max(v.y for v in vs))/2
            detail=g.tube('Worn stair scratch',[(x-.18,y-.06,z),(x-.08,y-.045,z),(x+.02,y-.065,z)],.004,'stone_dark',4)
            detail.parent=obj.parent
    g.CURRENT['modeling_stage']='reference_detail_pass'


def studio_finish():
    style_blender.preview(bpy.context.scene)


def component_light_cues(kind):
    if kind.startswith('mushroom'):
        # Small luminous shapes are baked into the asset rather than lights.
        for i in range(3):
            g.ico('Tiny floating glow spore',(.30*math.cos(i*2.1),-.38,.54+i*.17),(.018,)*3,'magic_core',2,0)
