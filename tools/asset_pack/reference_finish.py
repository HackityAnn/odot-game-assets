"""Reference refinement: saturated palette, carved surfaces and portable light cues.

All lighting accents are small authored meshes/materials, so the GLB keeps them
without depending on Blender lights, compositing or game-specific shaders.
"""
import math
import re
import bpy
import geometry as g


def palette():
    colors={
        'wood':(.36,.18,.075),'wood_light':(.56,.30,.12),'wood_edge':(.74,.43,.18),
        'wood_dark':(.17,.085,.035),'bark':(.28,.13,.055),'bark_light':(.43,.23,.085),
        'roof_blue':(.08,.27,.48),'roof_blue_light':(.15,.38,.64),'roof_blue_dark':(.055,.18,.34),
        'wall':(.67,.63,.50),'wall_light':(.83,.78,.63),
        'stone':(.40,.43,.42),'stone_light':(.56,.58,.53),'stone_dark':(.24,.28,.27),
        'grass':(.39,.57,.105),'grass_light':(.56,.71,.18),'grass_dark':(.22,.40,.055),
        'moss':(.28,.49,.07),'forest_leaf':(.20,.48,.13),'forest_leaf_light':(.41,.66,.12),
        'crystal_cyan':(.015,.61,.93),'crystal_blue':(.035,.19,.86),
        'crystal_light':(.20,.84,1),'crystal_purple':(.43,.065,.80),'crystal_lilac':(.66,.23,.97),
        'mushroom_blue':(.07,.13,.60),'mushroom_purple':(.35,.045,.63),
    }
    for name,color in colors.items():
        g.material(name,color,.3 if name.startswith('crystal') else .84,
                   emission=.25 if name.startswith('crystal') else .08 if name.startswith('mushroom') else 0)
    for name,color,emission in [
        ('contact_shadow',(.13,.20,.07),0),('carved_shadow',(.16,.20,.19),0),
        ('stone_edge',(.67,.69,.61),0),('crystal_edge',(.24,.84,1),1.2),
        ('magic_core',(.38,.94,1),3),('window',(1,.43,.045),2.6),
        ('window_hot',(1,.82,.18),2.1),('window_shade',(.69,.20,.012),.65),
        ('amber_spill',(.80,.37,.06),.35),('cyan_spill',(.09,.54,.52),.3),
        ('gill_glow',(.055,.65,.88),1.7),('rune_glow',(.10,.81,1),3.5),
        ('water',(.025,.41,.55),.15),('water_light',(.14,.75,.89),.65)]:
        g.material(name,color,.75,emission=emission)
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
    """Small split lines and bevel-like chips on visible facets."""
    obj.data.update()
    faces=[p for p in obj.data.polygons if p.normal.z>-.15 and p.normal.y<.5]
    for i,poly in enumerate(faces[::max(1,len(faces)//7)]):
        center=poly.center;normal=poly.normal
        vertices=[obj.data.vertices[j].co for j in poly.vertices]
        if len(vertices)<3:continue
        a=center.lerp(vertices[0],.52)+normal*.007
        b=center+normal*.007
        c=center.lerp(vertices[1],.35)+normal*.007
        g.tube('Fine stone fracture',[a,b,c],.006,'carved_shadow',4)
        if i%2==0:
            pts=[center.lerp(v,.28)+normal*.009 for v in vertices[:3]]
            g.mesh('Stone weathered facet chip',pts,[(0,1,2)],'stone_edge')


def contact_patch(pos,radius=.38,mat='contact_shadow'):
    # Concentric, opaque color bands suggest soft contact light/shadow without
    # transparent planes or custom shaders in the runtime.
    x,y,z=pos
    g.lathe('Authored contact '+mat,[(0,radius),(.002,radius)],mat,12,(x,y,z))


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
    scene=bpy.context.scene
    scene.render.resolution_x=scene.render.resolution_y=1200
    scene.cycles.samples=48
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25
    for obj in scene.objects:
        if obj.type=='LIGHT':
            if obj.name.startswith('Warm key'):obj.data.energy*=.84;obj.data.size=3.5
            elif obj.name.startswith('Soft sky'):obj.data.energy*=.65
    # Higher contrast deepens carved recesses while preserving broad colors.
    try:scene.view_settings.look='AgX - Medium High Contrast'
    except TypeError:pass


def component_light_cues(kind):
    if kind.startswith('mushroom'):
        patch=g.lathe('Mushroom cyan ground bounce',[(0,.20),(.004,.20)],'cyan_spill',12)
        patch.location=(0,0,.005)
        # Small luminous shapes are baked into the asset rather than lights.
        for i in range(3):
            g.ico('Tiny floating glow spore',(.30*math.cos(i*2.1),-.38,.54+i*.17),(.018,)*3,'magic_core',2,0)
    elif kind in ['crystal_blue','crystal_purple']:
        patch=g.lathe('Crystal ground reflection',[(0,.24),(.003,.24)],'cyan_spill',10)
        patch.location=(0,0,.007)
    elif kind=='lantern_post':
        patch=g.lathe('Lantern warm ground bounce',[(0,.24),(.003,.24)],'amber_spill',12)
        patch.location=(.26,-.06,.007)
    elif kind in ['boulder','tree_snag','rune_monolith']:
        patch=g.lathe('Rock root contact shade',[(0,.25),(.002,.25)],'contact_shadow',10)
        patch.location=(0,0,.004)
