"""Reusable mesh library. Instances copy objects and share the library mesh data.

Run in a background Blender worker to author shared_village_kit.blend. Other
builders append prototypes without linking them into their visible scene.
"""
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from mathutils import Matrix
import geometry as g

LIBRARY = g.ROOT/'sources/props/shared_village_kit.blend'
PROTOTYPES = {}


def palette():
    g.material('iron', (.20,.23,.26), .45, .45)
    g.material('rope', (.70,.57,.36))
    g.material('hair', (.70,.22,.035))
    g.material('hair_light', (.88,.34,.065))
    g.material('fur', (.91,.86,.72))
    g.material('roof_blue', (.15,.34,.54))
    g.material('roof_blue_light', (.23,.43,.64))
    g.material('roof_blue_dark', (.11,.27,.43))
    g.material('bone', (.85,.80,.67))
    g.material('evil_steel', (.17,.16,.20),.55,.25)
    g.material('evil_edge', (.37,.34,.38),.42,.35)
    g.material('evil_red', (.53,.065,.075))
    g.material('evil_red_light', (.70,.13,.12))
    g.material('evil_red_dark', (.29,.03,.045))
    g.material('evil_purple', (.19,.095,.22))
    g.material('evil_purple_light', (.28,.14,.31))
    g.material('evil_purple_dark', (.10,.04,.12))
    g.material('ember', (1,.065,.025),.45,emission=2.2)
    g.material('fire_core', (1,.65,.13),.45,emission=3.0)


def reset():
    PROTOTYPES.clear()
    palette()


def place(kind, pos=(0,0,0), scale=1, rotation=(0,0,0)):
    if kind not in PROTOTYPES:
        with bpy.data.libraries.load(str(LIBRARY), link=False) as (source, dest):
            dest.collections=['kit_'+kind]
        col=dest.collections[0]
        if col is None: raise ValueError('Unknown kit asset: '+kind)
        PROTOTYPES[kind]=col
    root=g.empty(kind+'_instance', pos)
    root.rotation_euler=rotation
    root.scale=(scale,)*3 if isinstance(scale,(int,float)) else scale
    root['kit_asset']=kind
    root['kit_source']='sources/props/shared_village_kit.blend'
    for original in PROTOTYPES[kind].objects:
        obj=original.copy()
        g.CURRENT.objects.link(obj)
        obj.parent=root
        obj.matrix_parent_inverse=Matrix.Identity(4)
        obj.matrix_basis=original.matrix_basis.copy()
        if kind=='roof_tile':
            g.enum(obj.material_slots[0], 'link', 'OBJECT')
            obj.material_slots[0].material=g.M[g.RNG.choice(['roof_blue','roof_blue','roof_blue_light','roof_blue_dark'])]
    return root


def stone_block():
    g.cube('Dressed limestone', (0,0,.14), (.43,.31,.28), 'wall_light', .035)


def open_barrel():
    g.lathe('Open barrel staves',[(0,.25),(.08,.28),(.30,.31),(.52,.28),(.59,.26)],'wood_light',12,caps=False)
    g.lathe('Inside barrel shadow',[(.25,.235),(.27,.235)],'wood_dark',12)
    g.lathe('Barrel inner lip',[(.54,.228),(.59,.228)],'wood_dark',12,caps=False)
    for z in [.07,.49]: g.torus('Open barrel iron hoop',(0,0,z),.286,.035,'silver_dark')
    g.torus('Open barrel rim',(0,0,.59),.247,.017,'wood_edge',sides=12)
    for i in range(12):
        a=i*math.tau/12
        g.beam('Open barrel stave seam',(.286*math.cos(a),.286*math.sin(a),.12),(.288*math.cos(a),.288*math.sin(a),.46),.009,.009,'wood_dark',0)


def open_crate():
    g.cube('Open crate floor',(0,0,.04),(.45,.45,.065),'wood_dark',.01)
    for i in range(3):
        for s in [-1,1]:
            g.cube('Open crate side plank',(0,s*.225,(i+.5)*.15),(.45,.045,.14),'wood_light',.008)
            g.cube('Open crate end plank',(s*.225,0,(i+.5)*.15),(.045,.45,.14),'wood_light',.008)
    for s in [-1,1]: g.beam('Open crate diagonal',(-.19,s*.252,.07),(.19,s*.252,.41),.055,.03,'wood_edge',.008)


def skull():
    shell=g.ico('Carved bone skull',(0,0,.405),(.39,.32,.355),'bone',3,.008)
    cutters=[g.ico('Eye socket cutter',(s*.16,-.265,.39),(.116,.15,.135),'black',3,0) for s in [-1,1]]
    nose=[(x,y,z) for y in [-.43,-.15] for x,z in [(-.062,.22),(.062,.22),(0,.345)]]
    cutters.append(g.mesh('Nasal cavity cutter',nose,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'black'))
    cutters.append(g.cube('Jaw cavity cutter',(0,-.28,.09),(.44,.20,.20),'black',.014))
    bpy.context.view_layer.objects.active=shell
    for cutter in cutters:
        mod=shell.modifiers.new('Carved skull cavity','BOOLEAN'); g.enum(mod,'operation','DIFFERENCE')
        g.enum(mod,'solver','EXACT'); mod.object=cutter
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
    for s in [-1,1]:
        g.ico('Socket darkness',(s*.16,-.215,.39),(.108,.08,.125),'black',2,0)
        g.ico('Bone cheek',(s*.26,-.15,.215),(.13,.15,.13),'bone',2,.006)
    g.mesh('Dark nasal inset',[(0,-.21,.337),(-.054,-.21,.23),(.054,-.21,.23)],[(0,1,2)],'black')
    for i in range(6): g.cube('Skull upper tooth',((i-2.5)*.060,-.263,.092),(.052,.093,.14+(i%2)*.015),'bone',.012)


def spike():
    g.lathe('Forged armor spike',[(0,.105),(.065,.12),(.33,0)],'evil_edge',4)


def roof_tile():
    g.cube('Soft edged blue roof tile', (0,0,0), (.39,.34,.07), 'roof_blue', .027)


def target():
    for s in [-1,1]:
        g.beam('Target tripod leg', (s*.27,.05,0), (s*.12,0,.91), .07,.07)
    g.beam('Target rear leg',(0,.39,0),(0,0,.91),.07,.07)
    for r,y,mat in [(.35,-.035,'wood_edge'),(.30,-.070,'cream'),(.22,-.09,'red'),(.13,-.112,'cream'),(.055,-.13,'red')]:
        g.tube('Target ring',[(0,y,.72),(0,y-.018,.72)],r,mat,24)


def spear():
    g.tube('Ash spear shaft',[(0,0,0),(0,0,1.30)],.025,'wood_light')
    g.mesh('Leaf spearhead',[(-.09,0,1.28),(0,-.035,1.42),(.09,0,1.28),(0,0,1.65),(0,.035,1.42)],
           [(0,1,3),(1,2,3),(2,4,3),(4,0,3),(0,4,2,1)],'silver_light')
    for z in [1.18,1.23,1.28]: g.torus('Spear binding',(0,0,z),.028,.012,'rope',sides=8)


def arrow():
    g.tube('Arrow shaft',[(0,0,0),(0,0,.78)],.015,'wood_edge',6)
    g.mesh('Arrow steel tip',[(-.046,0,.74),(.046,0,.74),(0,-.025,.75),(0,0,.89)],
           [(0,1,3),(1,2,3),(2,0,3),(0,2,1)],'silver')
    for a in [0,math.pi/2]:
        ob=g.mesh('Arrow feather',[(-.055,0,.07),(0,0,.01),(.055,0,.07),(0,0,.22)],[(0,1,3),(1,2,3)],'cream')
        ob.data.transform(Matrix.Rotation(a,4,'Z'))


def mug():
    g.lathe('Tankard body',[(0,.085),(.16,.085)],'wood_light',10)
    for z in [.02,.14]: g.torus('Tankard band',(0,0,z),.087,.012,'silver_dark',sides=10)
    g.torus('Tankard handle',(.105,0,.085),.055,.016,'wood_edge','Y',12)
    g.lathe('Foam surface',[(.16,.074),(.18,.072)],'cream',12)
    for x,y in [(-.025,.025),(.03,0),(-.015,-.035)]: g.ico('Foam bubble',(x,y,.18),(.033,.035,.021),'cream',2)


def book():
    g.cube('Book pages',(0,0,.046),(.23,.30,.067),'cream',.007)
    for z in [.01,.086]: g.cube('Blue leather cover',(0,0,z),(.26,.325,.02),'blue_dark',.006)
    g.cube('Book spine',(-.12,0,.048),(.025,.325,.07),'blue',.006)
    for y in [-.10,.10]: g.cube('Gold book clasp',(-.13,y,.05),(.022,.027,.074),'gold',.004)


def parcel():
    g.cube('Linen parcel',(0,0,.16),(.40,.32,.30),'cream',.055)
    for x in [-.01,.02]: g.cube('Parcel tie',(x,0,.16),(.02,.337,.32),'rope',.005)
    g.cube('Parcel cross tie',(0,0,.16),(.417,.018,.32),'rope',.005)


def bench():
    for y in [-.085,.085]: g.cube('Bench seat',(0,y,.38),(1.05,.165,.085),'wood_light',.02)
    for x in [-.37,.37]:
        g.cube('Bench trestle',(x,0,.19),(.10,.30,.38),'wood',.02)
    g.beam('Bench stretcher',(-.40,0,.15),(.40,0,.15),.06,.075,'wood_edge')


def axe():
    g.tube('Axe ash handle',[(0,0,-.28),(.015,0,.25),(.025,0,.70)],[.044,.043,.039],'wood_light',10)
    g.tube('Leather axe grip',[(0,0,-.19),(0,0,.15)],.052,'leather',10)
    for z in [-.16,-.10,-.04,.02,.08,.14]: g.torus('Grip wrapping',(0,0,z),.052,.009,'leather_light',sides=10)
    outline=[(-.09,.66),(.15,.72),(.40,.84),(.52,.71),(.48,.47),(.36,.33),(.17,.46),(-.09,.49)]
    verts=[(x,y,z) for y in [-.055,.055] for x,z in outline]; n=len(outline)
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    g.mesh('Forged crescent axe blade',verts,faces,'silver',.018)
    edge=[outline[i] for i in [2,3,4,5,6]]
    verts=[(x,y,z) for y in [-.058,.058] for x,z in edge]
    g.mesh('Sharpened axe cutting edge',verts,[tuple(range(5)),tuple(range(5,10))]+[(i,i+1,i+6,i+5) for i in range(4)],'silver_light',.009)
    g.cube('Iron axe socket',(.02,0,.59),(.12,.16,.20),'silver_dark',.025)


BUILDERS={'barrel':lambda:g.barrel((0,0,0)), 'crate':lambda:g.crate((0,0,0)),
          'open_barrel':open_barrel, 'open_crate':open_crate,
          'skull':skull, 'spike':spike,
          'lantern':lambda:g.lantern((0,0,0)), 'shrub':lambda:g.shrub((0,0,0)),
          'pine':lambda:g.pine((0,0,0)), 'stone_block':stone_block, 'roof_tile':roof_tile,
          'target':target, 'spear':spear, 'arrow':arrow, 'mug':mug, 'book':book,
          'parcel':parcel, 'bench':bench, 'axe':axe,
          'cannonball':lambda:g.ico('Iron cannonball',(0,0,.12),(.12,)*3,'iron',2,.005)}


def main():
    g.clear_scene(); palette()
    for i,(name,builder) in enumerate(BUILDERS.items()):
        col=g.collection('kit_'+name); g.target(col); builder()
        col.asset_mark(); col.asset_data.description='Reusable original village prop: '+name
        col['kit_version']=1
        # Apply edge modifiers once in the library; every placed copy shares the result.
        for obj in col.objects:
            if obj.type!='MESH': continue
            bpy.context.view_layer.objects.active=obj
            for modifier in list(obj.modifiers): bpy.ops.object.modifier_apply(modifier=modifier.name)
        # The editable prototypes retain origin zero; collection instances make
        # the library itself a readable grid without changing placement semantics.
        col.use_fake_user=True
        bpy.context.scene.collection.children.unlink(col)
        display=bpy.data.objects.new('Display — '+name,None)
        bpy.context.scene.collection.objects.link(display)
        display.instance_type='COLLECTION'; display.instance_collection=col
        display.location=((i%4-1.5)*2.1,(1.5-i//4)*2.1,0)
    g.studio(.7,12)
    bpy.context.scene.name='Shared village kit — append asset collections'
    bpy.ops.wm.save_as_mainfile(filepath=str(LIBRARY))
    print('Saved',len(BUILDERS),'reusable prop collections:',LIBRARY)


if __name__=='__main__': main()
