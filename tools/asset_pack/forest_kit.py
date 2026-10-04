"""Reusable magical forest components; baked prototypes with shared mesh instances.

Author explicitly with the worker runner. Checking/exporting never calls builders.
Each collection has an origin at the placement point and is independently exportable.
"""
import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
from mathutils import Matrix, Vector
import geometry as g
import reference_finish as finish

LIBRARY=g.ROOT/'sources/environment/shared_forest_kit.blend'
PROTOTYPES={}
RADIUS=2.55
HEIGHT=math.sqrt(3)*RADIUS/2


def palette():
    for name,color,glow in [
        ('crystal_cyan',(.03,.67,1),.35),('crystal_blue',(.08,.27,.95),.25),
        ('crystal_light',(.30,.91,1),.7),('crystal_purple',(.53,.12,.92),.3),
        ('crystal_lilac',(.76,.36,1),.5),('rune_glow',(.28,.95,1),3.0),
        ('mushroom_blue',(.16,.25,.81),.20),('mushroom_purple',(.53,.16,.80),.20),
        ('gill_glow',(.28,.86,.97),1.5),('water',(.10,.66,.80),.25),
        ('water_light',(.35,.89,.98),.9),('moss',(.39,.58,.12),0),
        ('forest_leaf',(.32,.62,.22),0),('forest_leaf_light',(.57,.76,.23),0)]:
        g.material(name,color,.35 if name.startswith(('crystal','water')) else .8,emission=glow)


def reset():
    PROTOTYPES.clear();palette()


def place(kind,pos=(0,0,0),scale=1,rotation=(0,0,0)):
    if kind not in PROTOTYPES:
        with bpy.data.libraries.load(str(LIBRARY),link=False) as (_,dest):
            dest.collections=['forest_'+kind]
        if dest.collections[0] is None:raise ValueError('Unknown forest component: '+kind)
        PROTOTYPES[kind]=dest.collections[0]
    root=g.empty(kind+'_instance',pos);root.rotation_euler=rotation
    root.scale=(scale,)*3 if isinstance(scale,(int,float)) else scale
    root['kit_asset']='forest_'+kind;root['kit_source']='sources/environment/shared_forest_kit.blend'
    for original in PROTOTYPES[kind].objects:
        obj=original.copy();g.CURRENT.objects.link(obj);obj.parent=root
        obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=original.matrix_basis.copy()
    return root


def crystal(purple=False):
    sides=5
    verts=[(r*math.cos(i*math.tau/sides+.2),r*math.sin(i*math.tau/sides+.2),z)
           for z,r in [(0,.19),(.27,.30),(.76,.28),(1.17,.27)] for i in range(sides)]
    verts.append((.065,-.035,1.64))
    faces=[tuple(reversed(range(sides)))]
    for j in range(3):
        for i in range(sides):
            a=j*sides+i;b=j*sides+(i+1)%sides;c=(j+1)*sides+(i+1)%sides;d=(j+1)*sides+i
            faces.extend([(a,b,d),(b,c,d)] if (j+i)%2 else [(a,b,c),(a,c,d)])
    faces += [(15+i,15+(i+1)%sides,20) for i in range(sides)]
    obj=g.mesh('Faceted magical crystal',verts,faces,'crystal_purple' if purple else 'crystal_cyan')
    g.facet_colors(obj,['crystal_purple','crystal_lilac','crystal_blue'] if purple else ['crystal_cyan','crystal_blue','crystal_light'])


def mushroom(purple=False,small=False):
    stem=g.lathe('Curving luminous mushroom stem',[(0,.15),(.23,.20),(.64,.14),(1.14,.17)],'gill_glow',10)
    for v in stem.data.vertices:v.co.x+=.14*math.sin(v.co.z*2.4)
    cap=g.lathe('Broad faceted mushroom cap',[(0,.74),(.12,.87),(.30,.76),(.58,.53),(.74,.12),(.76,0)],'mushroom_purple' if purple else 'mushroom_blue',16,(.08,0,1.08))
    g.facet_colors(cap,['mushroom_purple','crystal_purple'] if purple else ['mushroom_blue','crystal_blue'])
    g.lathe('Luminous cap underside',[(0,.74),(.06,.70)],'gill_glow',12,(.08,0,1.075))
    for i in range(12):
        a=i*math.tau/12
        g.tube('Mushroom radial gill',[(.08+.15*math.cos(a),.15*math.sin(a),1.075),(.08+.70*math.cos(a),.70*math.sin(a),1.075)],.012,'crystal_light',4)
    for x,y,r in [(-.36,-.46,.10),(.39,-.42,.085),(0,-.68,.08),(-.20,.20,.09),(.38,.18,.11),(.02,-.10,.065),(-.57,-.18,.075),(.60,.08,.07)]:
        radius=math.hypot(x,y)
        z=1.08+(.58+(.53-radius)*.16/.41 if radius<.53 else .30+(.76-radius)*.28/.23)
        g.ico('Bioluminescent cap spot',(x+.08,y,z+.028),(r,r,.036),'rune_glow',2,0)
    if small:
        for obj in g.CURRENT.objects:
            if obj.type=='MESH':obj.data.transform(Matrix.Scale(.28,4))


def boulder():
    ob=g.ico('Angular mossy forest boulder',(0,0,.35),(.53,.43,.49),'stone',2,.13)
    g.facet_colors(ob,['stone','stone_light','stone_dark'])


def moss():
    for x,y,z in [(-.15,.03,.025),(.14,.06,.05),(.01,-.12,.01)]:
        g.ico('Soft moss patch',(x,y,z),(.22,.19,.09),'moss',1,.06)


def leaves():
    for i in range(6):
        a=i*math.tau/6
        rot=Matrix.Rotation(a,4,'Z')
        verts=[rot @ Vector(v) for v in [(0,0,.04),(-.12,.18,.15),(0,.42,.17),(.12,.18,.15),(0,.17,.23)]]
        g.mesh('Broad woodland leaf',verts,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],'forest_leaf' if i%2 else 'forest_leaf_light')


def fern():
    for side in [-1,1]:
        for k in range(3):
            angle=side*(.6+k*.50);dx=.34*math.sin(angle);dy=.34*math.cos(angle)
            g.tube('Fern central stem',[(0,0,0),(dx*.5,dy*.5,.30),(dx,dy,.55)],.016,'forest_leaf',5)
            for i in range(4):
                t=(i+1)/5;x,y,z=dx*t,dy*t,.55*t
                for s in [-1,1]:
                    g.mesh('Fern leaflet',[(x,y,z),(x+s*.14*(1-t),y-.03,z+.055),(x+s*.07*(1-t),y+.07,z+.08)],[(0,1,2)],'forest_leaf_light')
    points=[(.09+.10*math.cos(t),-.09,.49+.10*math.sin(t)) for t in [i*.35 for i in range(16)]]
    g.tube('Curled fern fiddlehead',[(0,-.09,0),(.18,-.09,.39),*points],.021,'forest_leaf',6)


def root():
    g.tube('Gnarled exposed root',[(0,0,.15),(.25,.08,.12),(.56,-.03,.08),(.94,-.18,.025)],[.16,.13,.09,.025],'bark',7)
    g.tube('Root fork',[(.28,.07,.11),(.51,.32,.055),(.79,.37,.015)],[.09,.06,.015],'bark_light',6)


def snag():
    g.tube('Ancient twisting trunk',[(0,0,0),(.18,.03,.56),(.0,.08,1.19),(.22,.05,1.72)],[.34,.27,.24,.15],'bark',8)
    for s in [-1,1]:g.tube('Broken woodland branch',[(.08,0,.8),(.48*s,.06,1.31),(.61*s,.07,1.53)],[.13,.08,.025],'bark_light',7)
    for i in range(5):
        a=i*math.tau/5
        g.tube('Tree buttress root',[(0,0,.25),(.52*math.cos(a),.52*math.sin(a),.08),(.84*math.cos(a),.84*math.sin(a),.02)],[.16,.09,.025],'bark',7)


def diamond(pos=(0,-.105,.52),scale=1):
    x,y,z=pos
    g.tube('Glowing diamond rune',[(x,y,z+.23*scale),(x+.115*scale,y,z),(x,y,z-.23*scale),(x-.115*scale,y,z),(x,y,z+.23*scale)],.014*scale,'rune_glow',6)
    g.tube('Rune vertical stroke',[(x,y,z-.43*scale),(x,y,z+.43*scale)],.012*scale,'rune_glow',6)


def monolith():
    rings=[(0,.30),(.50,.37),(1.17,.34),(1.62,.21)]
    obj=g.lathe('Weathered shrine monolith',rings,'stone',7,(0,.13,0))
    for vertex in obj.data.vertices:
        if vertex.co.z>.2:vertex.co.z+=g.RNG.uniform(-.08,.08)
    g.facet_colors(obj,['stone','stone_light'])
    # Flat inset puts the engraving clearly in front of the stone's facet plane.
    g.cube('Flat engraved rune face',(0,-.25,.85),(.40,.045,1.05),'stone_dark',.035)
    diamond((0,-.279,.86),1.5)


def rune_circle():
    g.torus('Shrine magic circle',(0,0,.015),.48,.018,'rune_glow',sides=32)
    g.torus('Shrine inner glyph circle',(0,0,.02),.18,.015,'rune_glow',sides=24)
    for i in range(6):
        a=i*math.tau/6
        g.tube('Radial shrine marking',[(.32*math.cos(a),.32*math.sin(a),.022),(.41*math.cos(a),.41*math.sin(a),.022)],.012,'rune_glow',5)


def plinth():
    g.lathe('Shrine stone pedestal',[(0,.79),(.16,.79),(.22,.74)],'stone_dark',10)
    for i in range(8):
        a=i*math.tau/8;b=(i+1)*math.tau/8-.025
        verts=[(r*math.cos(t),r*math.sin(t),z) for z in [.22,.35] for r,t in [(.0,a),(.75,a),(.75,b),(.0,b)]]
        g.mesh('Radial shrine paving stone',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'stone_light',.015)


def lantern_post():
    g.cube('Woodland lantern upright',(0,0,.79),(.14,.14,1.58),'wood_light')
    g.beam('Woodland lantern bracket',(-.04,0,1.55),(.40,0,1.55),.13,.13,'wood_edge')
    g.tube('Lantern chain',[(.32,0,1.54),(.32,0,1.31)],.016,'wood_dark')
    g.lantern((.32,0,1.06),1.10)


def arch_block():
    # One wedge; recipes arrange rotated instances into a true open bridge arch.
    a=-math.pi/22;b=math.pi/22
    verts=[(r*math.sin(t),y,r*math.cos(t)) for y in [-.20,.20] for r,t in [(.61,a),(.61,b),(.86,b),(.86,a)]]
    g.mesh('Stone bridge arch voussoir',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'stone_light',.016)


def plank():
    g.cube('Bridge deck plank',(0,0,0),(.16,1.0,.10),'wood_light',.015)
    for y in [-.35,.35]:g.ico('Deck iron nail',(0,y,.055),(.016,.016,.008),'silver_dark',1,0)


def bridge_post():
    g.cube('Bridge rail upright',(0,0,.37),(.17,.17,.74),'wood_light',.02)
    g.cube('Bridge post cap',(0,0,.75),(.24,.24,.13),'wood_edge',.025)


def bridge_rail():
    g.cube('Bridge timber rail',(0,0,0),(1.02,.10,.12),'wood_edge',.02)


def stone_block():
    g.cube('Forest bridge dressed stone',(0,0,.12),(.30,.24,.24),'stone_light',.026)


def hex_layer(name,z0,z1,mat):
    return g.lathe(name,[(z0,RADIUS),(z1,RADIUS)],mat,6)


def hex_meadow():
    hex_layer('Standard hex stone foundation',-.36,-.13,'base')
    hex_layer('Standard hex earth layer',-.13,-.04,'soil')
    hex_layer('Standard hex meadow top',-.04,0,'grass')


def bank_polygon(sign):
    points=[(RADIUS*math.cos(i*math.tau/6),RADIUS*math.sin(i*math.tau/6)) for i in range(6)]
    cut=.46;out=[]
    for p,q in zip(points,points[1:]+points[:1]):
        inside=p[0]*sign>=cut;next_inside=q[0]*sign>=cut
        if inside:out.append(p)
        if inside!=next_inside:
            t=(sign*cut-p[0])/(q[0]-p[0]);out.append((sign*cut,p[1]+t*(q[1]-p[1])))
    return out


def prism(name,outline,z0,z1,mat):
    n=len(outline);verts=[(x,y,z) for z in [z0,z1] for x,y in outline]
    return g.mesh(name,verts,[tuple(reversed(range(n))),tuple(range(n,2*n)),*[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]],mat)


def hex_stream():
    hex_layer('River hex stone foundation',-.36,-.27,'base')
    hex_layer('River hex bed',-.27,-.23,'soil')
    for sign in [-1,1]:
        bank=bank_polygon(sign)
        prism('Cut river bank',bank,-.23,-.04,'soil')
        prism('Meadow river bank',bank,-.04,0,'grass')
    g.cube('Continuous river water',(0,0,-.18),(.91,HEIGHT*2,.025),'water',0)


def waterfall():
    g.mesh('Opaque stylized waterfall',[(-.36,.0,0),(.36,.0,0),(.38,-.13,-.10),(.35,-.18,-.48),(-.35,-.18,-.48),(-.38,-.13,-.10)],[(0,1,2,5),(5,2,3,4)],'water_light')
    for x in [-.26,-.1,.13,.27]:g.tube('Waterfall foam streak',[(x,-.012,.002),(x,-.142,-.11),(x,-.192,-.46)],.012,'crystal_light',5)


def foam():
    for x,y,r in [(-.14,.0,.11),(.09,.06,.13),(.21,-.11,.06)]:g.torus('River foam ripple',(x,y,0),r,.012,'water_light',sides=16)


def component_details(kind):
    if kind in ['boulder','rune_monolith']:
        for obj in list(g.CURRENT.objects):
            if obj.type=='MESH' and obj.name.startswith(('Angular mossy','Weathered shrine')):
                finish.rock_finish(obj)
    elif kind.startswith('crystal'):
        for i in [2,3,4]:
            a=i*math.tau/5+.2
            g.tube('Crystal sharp reflected edge',[(.30*math.cos(a),.30*math.sin(a),.27),(.27*math.cos(a),.27*math.sin(a),1.17),(.065,-.035,1.64)],.006,'crystal_edge',5)
        g.ico('Crystal bright tip gleam',(.065,-.035,1.635),(.025,)*3,'magic_core',2,0)
    elif kind.startswith('mushroom'):
        size=.28 if kind=='mushroom_small' else 1
        for i in range(10):
            a=i*math.tau/10
            points=[(.15*math.cos(a)*size,.15*math.sin(a)*size,.05*size),((.14*math.cos(a)+.12)*size,.14*math.sin(a)*size,.63*size)]
            g.tube('Mushroom translucent stem groove',points,.005*size,'crystal_light',4)
    elif kind in ['root','tree_snag']:
        if kind=='root':
            for y in [-.06,.03]:g.tube('Root bark carved grain',[(.12,y,.27),(.34,y+.025,.22),(.61,y-.04,.15),(.79,y-.12,.09)],.006,'wood_dark',4)
        else:
            for x in [-.10,.04,.16]:g.tube('Tree bark carved groove',[(x,-.26,.12),(x+.08,-.21,.61),(x,-.14,1.15),(x+.13,-.07,1.55)],.009,'wood_dark',4)
    elif kind=='bridge_plank':
        for y in [-.24,.15]:g.tube('Deck plank grain',[(.013,y-.15,.052),(.028,y,.052),(.01,y+.17,.052)],.004,'wood_dark',4)
        g.beam('Plank edge shadow',(-.077,-.46,-.043),(-.077,.46,-.043),.01,.015,'wood_dark',.002)
    elif kind=='bridge_post':
        g.cube('Post cap contact shadow',(0,0,.708),(.182,.182,.022),'wood_dark',.005)
        for z in [.23,.60]:g.ico('Bridge post iron peg',(0,-.088,z),(.025,.013,.025),'silver_dark',2,0)
        for x in [-.037,.039]:g.tube('Bridge post fine grain',[(x,-.088,.08),(x+.007,-.088,.37),(x-.004,-.088,.67)],.004,'wood_dark',4)
    elif kind=='bridge_rail':
        g.cube('Rail underside shadow',(0,0,-.052),(1.01,.105,.014),'wood_dark',.003)
    elif kind in ['stone_block','stone_arch_block']:
        for obj in list(g.CURRENT.objects):
            if obj.type=='MESH':finish.rock_finish(obj)
    elif kind=='lantern_post':
        for x in [-.04,.04]:g.tube('Lantern post grain',[(x,-.074,.08),(x+.009,-.074,.78),(x-.006,-.074,1.43)],.005,'wood_dark',4)
        g.cube('Lantern hot glass inset',(.32,-.089,1.075),(.096,.014,.14),'window_hot',.008)
    elif kind=='shrine_plinth':
        g.torus('Shrine rim contact shadow',(0,0,.222),.60,.008,'carved_shadow',sides=32)
    elif kind=='rune_diamond':
        g.ico('Rune center luminous seed',(0,-.12,.52),(.028,)*3,'magic_core',2,0)
    elif kind=='rune_circle':
        for i in range(8):
            a=i*math.tau/8
            g.ico('Magic circle luminous node',(.48*math.cos(a),.48*math.sin(a),.024),(.025,.025,.008),'magic_core',2,0)
    elif kind=='leaf_clump':
        for i in range(6):
            a=i*math.tau/6
            g.tube('Leaf central vein',[(0,0,.05),(.17*math.sin(a),.17*math.cos(a),.233),(.38*math.sin(a),.38*math.cos(a),.19)],.004,'grass_dark',4)
    elif kind=='fern':
        for x in [-.07,.07]:g.ico('Fern unfolding leaf tip',(x,.24,.57),(.028,.055,.018),'forest_leaf_light',2,0)
    elif kind=='moss':
        for x,y in [(-.24,.04),(.26,.07),(.03,-.26)]:g.ico('Moss tiny sprouting mound',(x,y,.025),(.06,.065,.055),'grass_light',2,.04)
    elif kind=='hex_meadow':
        for i in range(6):
            a=i*math.tau/6;b=(i+1)*math.tau/6
            p=(RADIUS*math.cos(a),RADIUS*math.sin(a),-.045)
            q=(RADIUS*math.cos(b),RADIUS*math.sin(b),-.045)
            g.beam('Thin meadow rim shadow',p,q,.008,.010,'grass_dark',0)
    elif kind=='foam':
        for i in range(5):g.ico('Foam bead',((i-2)*.085,.12+.035*(i%2),.014),(.02,.026,.012),'crystal_light',2,0)
    elif kind=='waterfall':
        for x in [-.18,.06,.20]:g.tube('Waterfall fine streak',[(x,-.016,-.025),(x,-.155,-.14),(x,-.19,-.42)],.005,'magic_core',4)
    elif kind=='hex_stream':
        for y in [-1.74,-.93,.24,1.17,1.88]:
            g.tube('River reflected current',[(-.30,y,-.163),(-.10,y+.06,-.163),(.17,y+.04,-.163)],.005,'water_light',4)


BUILDERS={
    'crystal_blue':crystal,'crystal_purple':lambda:crystal(True),
    'mushroom_blue':mushroom,'mushroom_purple':lambda:mushroom(True),
    'mushroom_small':lambda:mushroom(False,True),'boulder':boulder,'moss':moss,
    'leaf_clump':leaves,'fern':fern,'root':root,'tree_snag':snag,
    'rune_monolith':monolith,'rune_diamond':diamond,'rune_circle':rune_circle,
    'shrine_plinth':plinth,'lantern_post':lantern_post,
    'stone_arch_block':arch_block,'stone_block':stone_block,'bridge_plank':plank,
    'bridge_post':bridge_post,'bridge_rail':bridge_rail,
    'hex_meadow':hex_meadow,'hex_stream':hex_stream,'waterfall':waterfall,'foam':foam,
}


def main():
    g.clear_scene();reset();finish.palette()
    for i,(kind,builder) in enumerate(BUILDERS.items()):
        col=g.collection('forest_'+kind);g.target(col);builder()
        component_details(kind)
        finish.component_light_cues(kind)
        for obj in col.objects:
            if obj.type=='MESH':
                bpy.context.view_layer.objects.active=obj
                for mod in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
        col.asset_mark();col.asset_data.description='Reusable magical forest component: '+kind
        col['placement_origin']='local origin; meadow surface z=0';col.use_fake_user=True
        bpy.context.scene.collection.children.unlink(col)
        display=bpy.data.objects.new('Display '+kind,None);bpy.context.scene.collection.objects.link(display)
        display.instance_type='COLLECTION';display.instance_collection=col
        display.location=((i%5-2)*5.8,(2-i//5)*5.8,0)
    g.studio(.8,34)
    bpy.ops.wm.save_as_mainfile(filepath=str(LIBRARY))
    print('Saved',len(BUILDERS),'reusable forest components')


if __name__=='__main__':main()
