"""Shared original chibi body, three costumes, removable props, and animation rig."""
import math
import bpy
from mathutils import Matrix, Vector
import geometry as g
import art_style as style

WEIGHTS = []
PROP_COLLECTION = None


def weighted(obj, bone):
    WEIGHTS.append((obj,bone))
    return obj


def part(name,pos,size,mat,bone,bevel=.04,rot=None):
    return weighted(g.cube(name,pos,size,mat,bevel,rot),bone)


def ball(name,pos,size,mat,bone,subdivisions=2):
    obj=g.ico(name,pos,size,mat,subdivisions,.012)
    # Rounded clay faces and gloves sit alongside faceted armor and cloth.
    if mat in style.UNITS.rounded_materials:
        for polygon in obj.data.polygons: polygon.use_smooth=True
    return weighted(obj,bone)


def limb(name,a,b,radii,mat,bone):
    return weighted(g.tube(name,[a,b],radii,mat,10),bone)


def buckle(pos,size=.18,bone='pelvis'):
    x,y,z=pos
    part('Gold belt buckle',(x,y,z),(size,.04,size),'gold',bone,.015)
    part('Buckle opening',(x,y-.024,z),(size*.60,.012,size*.54),'leather',bone,.006)
    part('Buckle tongue',(x,y-.035,z),(size*.72,.015,.021),'gold_light',bone,.004)


def eyes(mage=False):
    for x in [-.14,.14]:
        if mage:
            ball('Glowing mage eye',(x,-.402,2.065),(.047,.026,.084),'magic','head',2)
        else:
            part('Black oval eye',(x,-.405,2.065),(.071,.024,.145),'black','head',.030)


def body(kind):
    cloth={'knight':'blue','mage':'purple','archer':'green'}[kind]
    ball('Chibi face',(0,-.018,2.015),(.425,.395,.445),'face_dark' if kind=='mage' else 'skin','head',3)
    if kind!='mage':
        for x in [-.414,.414]: ball('Small ear',(x,-.025,2.03),(.085,.074,.11),'skin','head')
    eyes(kind=='mage')
    limb('Neck',(0,0,1.48),(0,0,1.77),[.14,.17],'skin' if kind!='mage' else 'face_dark','spine')
    torso=weighted(g.lathe('Tapered tunic',[(.79,.295),(.96,.32),(1.38,.43),(1.52,.34)],cloth,10),'spine')
    # Tunic is deliberately broader across X than Y.
    for vertex in torso.data.vertices: vertex.co.y*=.69
    part('Leather belt',(0,-.01,.94),(.70,.47,.105),'leather','pelvis',.035)
    buckle((.0,-.271,.94),.20)
    for side,x in [('L',.235),('R',-.235)]:
        limb('Trouser thigh',(x,0,.80),(x,-.015,.48),[.17,.145],'leather',f'thigh.{side}')
        limb('Trouser shin',(x,-.015,.48),(x,-.035,.19),[.145,.13],'leather',f'shin.{side}')
        part('Oversized leather boot',(x,-.13,.17),(.36,.54,.29),'leather',f'foot.{side}',.09)
        part('Boot sole',(x,-.14,.055),(.375,.56,.07),'wood_dark',f'foot.{side}',.025)
        part('Boot cuff',(x,-.025,.34),(.34,.33,.12),'leather_light',f'shin.{side}',.035)
    for side,sgn in [('L',1),('R',-1)]:
        a=(sgn*.39,0,1.43); b=(sgn*.60,-.005,1.16); c=(sgn*.76,-.08,.94)
        ball('Rounded tunic shoulder',a,(.22,.24,.225),cloth,f'upper_arm.{side}')
        limb('Upper sleeve',a,b,[.19,.155],cloth,f'upper_arm.{side}')
        limb('Forearm sleeve',b,c,[.155,.12],cloth,f'forearm.{side}')
        limb('Leather wrist cuff',(sgn*.715,-.055,1.00),(sgn*.78,-.09,.91),[.135,.135],'leather_light',f'forearm.{side}')
        ball('Chibi glove',(sgn*.79,-.105,.885),(.145,.135,.155),
             'leather' if kind=='knight' else 'skin',f'hand.{side}')
        ball('Glove thumb',(sgn*.705,-.19,.90),(.073,.075,.10),
             'leather_light' if kind=='knight' else 'skin',f'hand.{side}')
    # The skirt is in two panels so legs remain readable and can swing independently.
    for side,sgn in [('L',1),('R',-1)]:
        part('Tunic skirt panel',(sgn*.18,-.04,.735),(.34,.43,.27),cloth,'pelvis',.025,(0,sgn*.09,0))
    for x in [-.28,.28]:
        part('Tunic gold edging',(x,-.27,.76),(.055,.035,.27),
             'gold' if kind!='archer' else 'green_light','pelvis',.012)


def helmet():
    # Upper helmet is rounded. Below the brow the front stays open to show the face.
    cap=weighted(g.lathe('Silver helmet crown',[(2.14,.48),(2.36,.46),(2.52,.31),(2.59,.10)],'silver',16),'head')
    for v in cap.data.vertices: v.co.y*=.91
    part('Helmet brow plate',(0,-.416,2.19),(.80,.095,.145),'silver_light','head',.04)
    for side,sgn in [('L',1),('R',-1)]:
        part('Helmet cheek guard',(sgn*.37,-.20,1.99),(.19,.28,.46),'silver','head',.035,(0,sgn*.12,0))
        weighted(g.torus('Helmet ear rim',(sgn*.484,.012,2.17),.10,.028,'gold','X',12),'head')
        limb('Helmet ear stud',(sgn*.49,.012,2.17),(sgn*.515,.012,2.17),[.067,.067],'silver_dark','head')
    part('Helmet nose guard',(0,-.47,2.07),(.095,.075,.30),'silver_light','head',.02)
    part('Helmet center ridge',(0,.02,2.515),(.10,.64,.09),'silver_light','head',.025)
    part('Plume gold mount',(0,.055,2.625),(.18,.22,.11),'gold','head',.025)
    plume=weighted(g.tube('Blue sweeping helmet plume',[(0,.06,2.67),(-.02,.12,2.93),(-.12,.18,3.11),(-.32,.15,3.16),(-.48,.06,3.02),(-.62,-.01,3.02)],
                          [.12,.21,.24,.21,.12,.015],'blue',9),'head')
    g.facet_colors(plume,['blue','blue_light','blue_dark'])


def hood(color):
    verts=[]; n=12
    # Oval shell with an actual open face. No geometry spans the opening.
    for y,rx,rz,cz in [(-.28,.545,.595,2.05),(-.43,.41,.455,2.045),(.18,.485,.53,2.08)]:
        for i in range(n):
            a=i*math.tau/n
            verts.append((rx*math.cos(a),y,cz+rz*math.sin(a)))
    verts.append((0,.46,2.10))
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(i,2*n+i,2*n+j,j),(2*n+i,3*n,2*n+j)])
    shell=weighted(g.mesh('Open cloth hood',verts,faces,color),'head')
    g.facet_colors(shell,[color,color+'_light'])
    # Visible collar frames the neck under the large hood.
    collar=weighted(g.lathe('Folded cloth collar',[(1.51,.25),(1.61,.39),(1.71,.30)],color,12),'spine')
    for v in collar.data.vertices: v.co.y*=.78


def cape(color):
    verts=[(-.33,.19,1.47),(.33,.19,1.47),(-.47,.42,1.06),(.47,.42,1.06),
           (-.62,.51,.51),(.62,.51,.51),(-.40,.58,.36),(0,.57,.44),(.40,.58,.36)]
    obj=weighted(g.mesh('Faceted travelling cape',verts,[(0,1,3,2),(2,3,5,7,4),(4,7,6),(7,5,8)],color),'spine')
    g.facet_colors(obj,[color,color+'_dark'])
    mod=obj.modifiers.new('Cape cloth thickness','SOLIDIFY'); mod.thickness=.045
    return obj


def wizard_hat():
    # Sculpted irregular rings give the cone a bent tip and a broad tilted brim.
    n=12; verts=[]
    rings=[(2.38,.77,0,0),(2.44,.70,0,0),(2.48,.41,0,0),
           (2.75,.34,-.05,.02),(3.03,.26,-.12,.04),(3.23,.18,-.25,.06),
           (3.29,.09,-.46,.065),(3.20,.012,-.67,.06)]
    for z,r,x,y in rings:
        for i in range(n):
            a=i*math.tau/n
            verts.append((x+r*math.cos(a),y+r*math.sin(a),z+.055*math.cos(a)))
    faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i)
           for j in range(len(rings)-1) for i in range(n)]
    faces += [tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))]
    hat=weighted(g.mesh('Bent purple wizard hat',verts,faces,'purple'),'head')
    g.facet_colors(hat,['purple','purple_light','purple_dark'])
    weighted(g.lathe('Wizard hat gold ribbon',[(2.55,.397),(2.69,.365)],'gold',12,(-.025,.008,0)),'head')
    part('Wizard hat ribbon buckle',(-.03,-.389,2.625),(.19,.045,.13),'gold_light','head',.012)


def sash(kind):
    color='gold' if kind=='knight' else 'leather_light'
    for a,b in [((-.35,-.215,1.44),(.29,-.253,.97)),((-.35,.22,1.44),(.29,.22,.97))]:
        weighted(g.beam('Diagonal shoulder strap',a,b,.07,.035,color,.01),'spine')
    if kind=='mage':
        part('Mage leather satchel',(-.39,-.28,.91),(.30,.17,.34),'leather','pelvis',.04)
        part('Satchel flap',(-.39,-.381,.99),(.32,.07,.13),'leather_light','pelvis',.025)
        part('Satchel brass clasp',(-.39,-.425,.91),(.055,.025,.065),'gold','pelvis',.008)
    if kind=='archer':
        part('Archer belt pouch',(.32,-.20,.86),(.20,.18,.25),'leather_light','pelvis',.035)


def weapon_target():
    g.target(PROP_COLLECTION)


def sword():
    weapon_target(); root=g.empty('sword')
    # Hand origin is the grip center, with the blade extending along local +Z.
    g.tube('Sword leather grip',[(0,0,-.16),(0,0,.16)],.058,'leather',8)
    for z in [-.12,-.055,.015,.08]: g.torus('Sword grip wrap',(0,0,z),.058,.009,'wood_dark',sides=10)
    g.ico('Sword pommel',(0,0,-.21),(.09,.065,.08),'gold',2)
    g.cube('Sword gold guard',(0,0,.20),(.48,.13,.105),'gold',.025)
    verts=[(-.125,-.025,.25),(.125,-.025,.25),(.105,-.025,1.10),(0,-.025,1.40),(-.105,-.025,1.10),
           (-.125,.025,.25),(.125,.025,.25),(.105,.025,1.10),(0,.025,1.40),(-.105,.025,1.10),
           (0,-.073,.25),(0,-.058,1.10),(0,.073,.25),(0,.058,1.10)]
    g.mesh('Sword broad faceted blade',verts,[(0,4,11,10),(10,11,2,1),(4,3,11),(11,3,2),
                (5,12,13,9),(12,6,7,13),(9,13,8),(13,7,8),(0,1,6,5),(0,5,9,4),(1,2,7,6),(4,9,8,3),(2,3,8,7)],'silver_light')
    for obj in list(PROP_COLLECTION.objects):
        if obj!=root and obj.parent is None: obj.parent=root
    return root


def shield():
    weapon_target(); root=g.empty('shield')
    outline=[(-.34,0,.48),(.34,0,.48),(.42,0,.05),(.28,0,-.33),(0,0,-.53),(-.28,0,-.33),(-.42,0,.05)]
    verts=[(x,-.035,z) for x,y,z in outline]+[(x,.055,z) for x,y,z in outline]
    faces=[tuple(reversed(range(7))),tuple(range(7,14))]+[(i,(i+1)%7,(i+1)%7+7,i+7) for i in range(7)]
    g.mesh('Shield blue field',verts,faces,'blue',.025)
    for i in range(7):
        a=Vector(outline[i]); b=Vector(outline[(i+1)%7]); a.y=b.y=-.075
        g.beam('Shield gold rim',a,b,.065,.055,'gold',.012)
    # Heraldic leaf/wing emblem: simple geometry, legible at small size.
    emblem=[(0,-.105,.32),(.08,-.105,.11),(.22,-.105,.17),(.17,-.105,-.02),
            (.05,-.105,-.08),(0,-.105,-.26),(-.05,-.105,-.08),(-.17,-.105,-.02),(-.22,-.105,.17),(-.08,-.105,.11)]
    g.mesh('Shield gold heraldry',emblem,[tuple(range(10))],'gold_light')
    g.cube('Shield hand grip',(0,.17,0),(.30,.12,.10),'leather',.03)
    for obj in list(PROP_COLLECTION.objects):
        if obj!=root and obj.parent is None: obj.parent=root
    return root


def staff():
    weapon_target(); root=g.empty('staff')
    g.tube('Wizard staff shaft',[(0,0,-.77),(.015,0,.30),(.065,0,.82)],[.055,.060,.095],'wood_light',9)
    for z in [-.1,.02,.14]: g.torus('Staff grip bindings',(0,0,z),.063,.018,'leather',sides=10)
    g.torus('Purple staff head',(0,0,1.04),.235,.053,'purple_light','Y',12,6)
    g.ico('Glowing magic crystal',(0,-.01,1.04),(.145,.10,.145),'magic',3,.01)
    for i in range(5):
        a=i*math.tau/5
        g.ico('Staff crystal prong',(.24*math.cos(a),0,1.04+.24*math.sin(a)),(.07,.06,.07),'purple',1)
    g.torus('Staff gold collar',(.046,0,.75),.095,.02,'gold',sides=12)
    for obj in list(PROP_COLLECTION.objects):
        if obj!=root and obj.parent is None: obj.parent=root
    return root


def bow():
    weapon_target(); root=g.empty('bow')
    points=[(-.04,0,-.78),(.11,0,-.57),(.21,0,-.34),(.245,0,0),(.20,0,.35),(.09,0,.58),(-.06,0,.78)]
    g.tube('Curved wooden bow',points,[.042,.052,.060,.065,.056,.05,.037],'wood_light',8)
    g.tube('Bowstring',[points[0],(-.20,0,0),points[-1]],.009,'cream',6)
    g.cube('Bow grip',(.24,0,0),(.11,.13,.23),'leather',.025)
    for obj in list(PROP_COLLECTION.objects):
        if obj!=root and obj.parent is None: obj.parent=root
    return root


def arrow():
    weapon_target(); root=g.empty('arrow')
    g.tube('Arrow shaft',[(-.56,0,0),(.87,0,0)],.013,'wood_edge',6)
    g.mesh('Arrowhead',[(.84,-.045,0),(1.07,0,0),(.84,.045,0),(.88,0,.035),(.88,0,-.035)],
           [(0,1,3),(3,1,2),(2,1,4),(4,1,0),(0,3,2,4)],'silver_light')
    for z in [-.035,.035]:
        g.mesh('Arrow feather',[(-.53,-.012,0),(-.35,-.012,0),(-.43,-.015,z*2),(-.58,-.015,z*2)],[(0,1,2,3)],'cream')
    for obj in list(PROP_COLLECTION.objects):
        if obj!=root and obj.parent is None: obj.parent=root
    return root


def quiver():
    # Quiver is worn equipment, bound to the torso; spare arrows are part of it.
    weighted(g.tube('Leather arrow quiver',[(-.24,.35,.87),(-.48,.34,1.72)],[.16,.19],'leather',10),'spine')
    for i in range(5):
        x=-.48+(i-2)*.06; y=.33+(i%2)*.08
        limb('Quiver spare arrow',(x+.13,y,1.26),(x-.075,y,2.13+(.06 if i%2 else 0)),[.018,.018],'wood_edge','spine')
        for sign in [-1,1]:
            weighted(g.mesh('Quiver white fletching',[(x-.08,y,2.02),(x-.12,y,2.22),
                         (x-.12+sign*.08,y,2.16),(x-.07+sign*.07,y,1.98)],[(0,1,2,3)],'cream'),'spine')


def create_rig(asset,leg_spread=0):
    g.target(asset)
    data=bpy.data.armatures.new('Chibi shared skeleton')
    rig=bpy.data.objects.new('rig',data); asset.objects.link(rig)
    bpy.context.view_layer.objects.active=rig; rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    definitions=[('root',(0,0,0),(0,0,.20),None),
                 ('pelvis',(0,0,.75),(0,0,1.02),'root'),
                 ('spine',(0,0,1.02),(0,0,1.52),'pelvis'),
                 ('neck',(0,0,1.52),(0,0,1.72),'spine'),
                 ('head',(0,0,1.72),(0,0,2.35),'neck')]
    for side,s in [('L',1),('R',-1)]:
        definitions += [(f'upper_arm.{side}',(s*.39,0,1.43),(s*.60,-.005,1.16),'spine'),
                        (f'forearm.{side}',(s*.60,-.005,1.16),(s*.76,-.08,.94),f'upper_arm.{side}'),
                        (f'hand.{side}',(s*.76,-.08,.94),(s*.83,-.105,.80),f'forearm.{side}'),
                        (f'weapon_socket.{side}',(s*.79,-.105,.885),(s*.79,-.105,1.035),f'hand.{side}'),
                        (f'thigh.{side}',(s*(.235+leg_spread),0,.80),(s*(.235+leg_spread),-.015,.48),'pelvis'),
                        (f'shin.{side}',(s*(.235+leg_spread),-.015,.48),(s*(.235+leg_spread),-.035,.19),f'thigh.{side}'),
                        (f'foot.{side}',(s*(.235+leg_spread),-.035,.19),(s*(.235+leg_spread),-.30,.13),f'shin.{side}')]
    for name,a,b,parent in definitions:
        bone=data.edit_bones.new(name); bone.head=a; bone.tail=b
        if parent: bone.parent=data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT'); rig.select_set(False)
    rig.show_in_front=True
    for obj,bone in WEIGHTS:
        # Bake only the modeling modifiers; preserve the armature in the exported mesh.
        bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers): bpy.ops.object.modifier_apply(modifier=modifier.name)
        group=obj.vertex_groups.new(name=bone)
        group.add(list(range(len(obj.data.vertices))),1.0,'REPLACE')
        modifier=obj.modifiers.new('Character skeleton','ARMATURE'); modifier.object=rig
        obj.parent=rig
    return rig


def equip(prop,rig,bone,location,rotation=(0,0,0)):
    from mathutils import Euler
    # Keep prop coordinates centered on the grip, and keep the parent inverse explicit.
    prop.parent=rig; g.enum(prop,'parent_type','BONE'); prop.parent_bone=bone
    if bone.startswith('weapon_socket.'): rig.data.bones[bone].use_deform=False
    desired=Matrix.Translation(Vector(location)) @ Euler(rotation).to_matrix().to_4x4() @ Matrix.Diagonal((*prop.scale,1))
    bpy.context.view_layer.update()
    # Blender bone parenting uses the bone tail as the parent-space origin.
    parent_matrix=rig.matrix_world @ rig.pose.bones[bone].matrix @ Matrix.Translation((0,rig.data.bones[bone].length,0))
    prop.matrix_parent_inverse=parent_matrix.inverted()
    prop.matrix_basis=desired


def reset_pose(rig):
    for bone in rig.pose.bones:
        g.enum(bone,'rotation_mode','XYZ')
        bone.rotation_euler=(0,0,0); bone.location=(0,0,0); bone.scale=(1,1,1)


def aim_pose(rig,strength):
    """Solve a readable bow-draw pose and bake it without runtime constraints."""
    p=rig.pose.bones
    for side,upper_direction,fore_direction in [('L',(1,-.1,.08),(1,0,.01)),
                                               ('R',(1,-.7,.5),(.97,.05,-.22))]:
        upper=p[f'upper_arm.{side}']; fore=p[f'forearm.{side}']; hand=p[f'hand.{side}']
        for bone,direction in [(upper,upper_direction),(fore,fore_direction)]:
            bpy.context.view_layer.update()
            start=bone.head.copy()
            rest=bone.bone.tail_local-bone.bone.head_local
            rotation=rest.rotation_difference(Vector(direction).normalized()).to_matrix().to_4x4()
            bone.matrix=Matrix.Translation(start) @ rotation @ bone.bone.matrix_local.to_3x3().to_4x4()
        bpy.context.view_layer.update()
        hand.matrix=Matrix.Translation(hand.head) @ hand.bone.matrix_local.to_3x3().to_4x4()
    for side in ['L','R']:
        for segment in ['upper_arm','forearm','hand']:
            bone=p[f'{segment}.{side}']
            bone.rotation_euler=tuple(angle*strength for angle in bone.rotation_euler)


def define_arm_stance(rig,directions):
    """Bake a costume's rest arm pose as offsets on the common skeleton."""
    reset_pose(rig)
    offsets={}
    for side,(upper_direction,fore_direction) in directions.items():
        for name,direction in [(f'upper_arm.{side}',upper_direction),(f'forearm.{side}',fore_direction)]:
            bone=rig.pose.bones[name]
            bpy.context.view_layer.update()
            rest=bone.bone.tail_local-bone.bone.head_local
            rotation=rest.rotation_difference(Vector(direction).normalized()).to_matrix().to_4x4()
            bone.matrix=Matrix.Translation(bone.head.copy()) @ rotation @ bone.bone.matrix_local.to_3x3().to_4x4()
        bpy.context.view_layer.update()
        hand=rig.pose.bones[f'hand.{side}']
        hand.matrix=Matrix.Translation(hand.head.copy()) @ hand.bone.matrix_local.to_3x3().to_4x4()
        for segment in ['upper_arm','forearm','hand']:
            bone=rig.pose.bones[f'{segment}.{side}']
            offsets[bone.name]=list(bone.rotation_euler)
    rig['rest_arm_offsets']=offsets
    reset_pose(rig)


def pose(rig,kind,clip,t):
    reset_pose(rig)
    p=rig.pose.bones
    wave=math.sin(t*math.tau)
    if clip=='idle':
        p['spine'].rotation_euler.x=.024*wave
        p['head'].rotation_euler.z=.025*wave
        p['pelvis'].location.y=.012*(1-math.cos(t*math.tau))
    elif clip in ['walk','run']:
        strength=.52 if clip=='walk' else .82
        for side,sign in [('L',1),('R',-1)]:
            leg=strength*wave*sign
            p[f'thigh.{side}'].rotation_euler.x=leg
            p[f'shin.{side}'].rotation_euler.x=-max(0,leg)*.8
            p[f'upper_arm.{side}'].rotation_euler.x=-leg*.65
            p[f'forearm.{side}'].rotation_euler.x=-.15-abs(leg)*.23
        p['pelvis'].location.y=.045*abs(wave)
        p['spine'].rotation_euler.x=.08 if clip=='walk' else .15
    elif clip=='attack':
        pulse=math.sin(math.pi*t)**2
        if kind=='knight':
            p['upper_arm.R'].rotation_euler.x=-1.05*pulse
            p['upper_arm.R'].rotation_euler.z=-.75*math.sin(t*math.pi*2)
            p['forearm.R'].rotation_euler.x=-.55*pulse
            p['spine'].rotation_euler.y=-.20*math.sin(t*math.pi*2)
            p['upper_arm.L'].rotation_euler.x=-.22*pulse
        elif kind=='mage':
            p['upper_arm.R'].rotation_euler.z=-.40*pulse
            p['upper_arm.R'].rotation_euler.x=-.75*pulse
            p['forearm.R'].rotation_euler.x=-.30*pulse
            p['upper_arm.L'].rotation_euler.x=-.85*pulse
            p['spine'].rotation_euler.x=-.06*pulse
        elif kind=='crossbow':
            p['spine'].rotation_euler.x=-.12*pulse
            p['forearm.R'].rotation_euler.x=-.15*pulse
            p['upper_arm.L'].rotation_euler.x=.06*pulse
        elif kind=='berserker':
            for side,sign in [('L',1),('R',-1)]:
                p[f'upper_arm.{side}'].rotation_euler.x=-1.25*pulse
                p[f'upper_arm.{side}'].rotation_euler.z=sign*.32*math.sin(t*math.pi*2)
                p[f'forearm.{side}'].rotation_euler.x=-.42*pulse
            p['spine'].rotation_euler.x=.16*pulse
        else:
            aim_pose(rig,pulse)
    elif clip=='hit':
        pulse=math.sin(math.pi*t)
        p['spine'].rotation_euler.x=-.28*pulse; p['head'].rotation_euler.x=-.12*pulse
        p['upper_arm.L'].rotation_euler.z=.15*pulse; p['upper_arm.R'].rotation_euler.z=-.15*pulse
    elif clip=='death':
        ease=t*t*(3-2*t)
        p['root'].rotation_euler.x=-1.40*ease
        p['root'].location.z=.24*ease
        p['spine'].rotation_euler.x=.13*ease
        p['upper_arm.L'].rotation_euler.z=.40*ease; p['upper_arm.R'].rotation_euler.z=-.40*ease
    for name,angles in rig.get('rest_arm_offsets',{}).items():
        for axis in range(3): p[name].rotation_euler[axis]+=angles[axis]


def animate(rig,kind):
    rig.animation_data_create()
    clips=style.CLIP_FRAMES
    actions={}
    for clip,last in clips.items():
        action=bpy.data.actions.new(clip); rig.animation_data.action=action
        action.use_fake_user=True
        # Dense, baked pose keys keep playback independent of Blender constraints.
        for frame in range(1,last+2):
            pose(rig,kind,clip,(frame-1)/last)
            for bone in rig.pose.bones:
                bone.keyframe_insert('rotation_euler',frame=frame,group=bone.name)
                bone.keyframe_insert('location',frame=frame,group=bone.name)
        action.use_frame_range=True; action.frame_start=1; action.frame_end=last+1
        slot=rig.animation_data.action_slot
        track=rig.animation_data.nla_tracks.new(); track.name=clip
        strip=track.strips.new(clip,1,action)
        if hasattr(strip,'action_slot'): strip.action_slot=slot
        track.mute=True
        actions[clip]=action
    rig.animation_data.action=actions['idle']
    bpy.context.scene.frame_start=1; bpy.context.scene.frame_end=style.CLIP_FRAMES['idle']+1
    bpy.context.scene.frame_set(1)
    reset_pose(rig)
    return actions


def build(kind,asset,props):
    global WEIGHTS,PROP_COLLECTION
    WEIGHTS=[]; PROP_COLLECTION=props
    g.target(asset)
    body(kind)
    if kind=='knight':
        helmet(); sash(kind)
        for side,s in [('L',1),('R',-1)]:
            ball('Silver shoulder pauldron',(s*.39,.0,1.48),(.235,.24,.19),'silver',f'upper_arm.{side}')
            part('Pauldron gold trim',(s*.48,-.12,1.38),(.20,.20,.065),'gold',f'upper_arm.{side}',.023)
            part('Silver forearm bracer',(s*.65,-.11,1.10),(.22,.10,.24),'silver',f'forearm.{side}',.035,(0,s*.30,0))
    elif kind=='mage':
        hood('purple'); cape('purple'); wizard_hat(); sash(kind)
    else:
        hood('green'); cape('green'); sash(kind); quiver()
    rig=create_rig(asset)
    if kind=='knight':
        sw=sword(); sh=shield()
        equip(sw,rig,'weapon_socket.R',(-.80,-.13,.885),(0,-.40,0))
        equip(sh,rig,'weapon_socket.L',(.79,-.27,1.04),(0,-.12,-.07))
    elif kind=='mage':
        st=staff(); equip(st,rig,'weapon_socket.L',(.84,-.12,.91),(0,.10,0))
    else:
        bw=bow(); ar=arrow()
        equip(bw,rig,'weapon_socket.L',(.81,-.16,.91),(0,.04,0))
        equip(ar,rig,'weapon_socket.R',(-.78,-.20,.90))
    animate(rig,kind)
    rig['animation_notes']=f'idle/walk/run loop; attack/hit/death one-shot; in-place locomotion; {style.UNITS.fps}fps'
    rig['forward']='-Y'; rig['shared_skeleton']='chibi_v1'
    return rig
