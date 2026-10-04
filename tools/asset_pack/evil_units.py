"""Initial evil faction models from the four user-supplied unit references.

Skulls and spikes share the village library; costumes and removable weapons use
the existing chibi skeleton. No assets or conventions come from the old game.
"""
import math
import bpy
from mathutils import Matrix, Vector
import geometry as g
import characters as c
import village_kit as kit

ATTACHMENTS=[]


def attached_part(kind,pos,scale,bone,rotation=(0,0,0)):
    root=kit.place(kind,scale=scale)
    root.name=kind+'_costume'
    # Bone parenting is applied after creating the rig, at the authored position.
    ATTACHMENTS.append((root,bone,pos,rotation))
    return root


def recolor(objects,mapping):
    for obj in objects:
        if obj.type!='MESH': continue
        for slot in obj.material_slots:
            name=slot.material.name.split('.')[0] if slot.material else ''
            if name in mapping:
                g.enum(slot,'link','OBJECT'); slot.material=g.M[mapping[name]]


def base_body(kind):
    mage=kind=='mage'; c.body('mage' if mage else 'knight')
    for obj,bone in list(c.WEIGHTS):
        discard=obj.name.startswith(('Black oval eye','Glowing mage eye','Small ear','Tunic gold edging'))
        if not mage and obj.name.startswith('Chibi face'): discard=True
        if kind in ['mage','berserker'] and obj.name.startswith(('Gold belt buckle','Buckle opening','Buckle tongue')): discard=True
        if discard:
            c.WEIGHTS.remove((obj,bone)); bpy.data.objects.remove(obj,do_unlink=True)
    recolor([obj for obj,bone in c.WEIGHTS],{'blue':'evil_steel','blue_light':'evil_edge','purple':'evil_purple','purple_light':'evil_purple_light','face_dark':'black'})
    if kind!='berserker':
        recolor([obj for obj,bone in c.WEIGHTS],{'skin':'black'})
    if mage:
        for s in [-1,1]:
            c.part('Angled ember eye',(s*.14,-.409,2.067),(.125,.025,.071),'ember','head',.020,(0,-s*.35,0))
    else:
        attached_part('skull',(0,-.022,1.73),1.0,'head')
        for s in [-1,1]: c.ball('Red skull eye',(s*.16,-.317,2.12),(.041,.025,.048),'ember','head',2)
    for side,s in [('L',1),('R',-1)]:
        c.part('Armored boot toe',(s*.235,-.285,.18),(.34,.21,.20),'evil_steel','foot.'+side,.04)
        c.part('Knee leather binding',(s*.235,-.09,.52),(.33,.22,.07),'leather_light','shin.'+side,.024)
        c.part('Dark wrist bracer',(s*.70,-.075,1.01),(.23,.24,.19),'evil_steel','forearm.'+side,.035,(0,s*.35,0))


def ragged_panel(bone='pelvis',front=True):
    y=-.30 if front else .26
    vertices=[(-.28,y,.94),(.28,y,.94),(.27,y,.53),(.18,y,.59),(.10,y,.46),
              (.04,y,.51),(0,y,.40),(-.11,y,.52),(-.19,y,.47),(-.26,y,.59)]
    ob=c.weighted(g.mesh('Tattered red tabard',vertices,[tuple(range(10))],'evil_red'),bone)
    mod=ob.modifiers.new('Cloth thickness','SOLIDIFY'); mod.thickness=.018


def horns(z=2.45):
    for s in [-1,1]:
        c.weighted(g.tube('Bent dark helmet horn',[(s*.41,.02,z),(s*.66,.02,z+.07),(s*.78,.015,z+.27),(s*.71,0,z+.51)],
                          [.115,.13,.09,.008],'evil_steel',7),'head')
        c.weighted(g.tube('Red horn tip',[(s*.76,.015,z+.29),(s*.71,0,z+.51)],[.084,.006],'evil_red',7),'head')


def helmet(horned=False):
    cap=c.weighted(g.lathe('Dark faceted helmet',[(2.30,.48),(2.42,.45),(2.57,.31),(2.65,.08)],'evil_steel',12),'head')
    for v in cap.data.vertices: v.co.y*=.90
    g.facet_colors(cap,['evil_steel','evil_edge'])
    c.part('Helmet iron brow',(0,-.425,2.31),(.77,.10,.14),'evil_edge','head',.024)
    c.part('Helmet central nasal ridge',(0,-.48,2.27),(.11,.10,.37),'evil_edge','head',.025)
    for s in [-1,1]:
        c.part('Helmet hanging cheek plate',(s*.36,-.19,2.02),(.16,.26,.43),'evil_steel','head',.025,(0,s*.10,0))
        c.weighted(g.torus('Helmet ear band',(s*.46,.035,2.30),.117,.025,'evil_edge','X',12),'head')
    if horned: horns(2.39)
    else:
        attached_part('spike',(0,0,2.60),1.10,'head')
        for s in [-1,1]: attached_part('spike',(s*.43,.02,2.32),.70,'head',(0,s*math.pi/2,0))


def armor(berserker=False):
    if not berserker:
        c.part('Dark breastplate',(0,-.08,1.29),(.74,.45,.41),'evil_steel','spine',.10)
    for s in [-1,1]:
        side='L' if s>0 else 'R'
        if berserker and s<0: continue
        c.ball('Heavy shoulder plate',(s*.41,0,1.49),(.25,.24,.17),'evil_steel','upper_arm.'+side,2)
        c.part('Shoulder plate rim',(s*.43,-.17,1.42),(.32,.065,.07),'evil_edge','upper_arm.'+side,.02)
        if not berserker or s==1: attached_part('spike',(s*.43,0,1.61),.76,'upper_arm.'+side,(0,s*.40,0))
    for a,b in [((-.33,-.32,1.46),(.29,-.31,1.04)),((.33,-.32,1.46),(-.29,-.31,1.04))]:
        c.weighted(g.beam('Crossed leather chest harness',a,b,.075,.035,'leather_light',.014),'spine')
    for x in [-.23,.23]:
        c.part('Armored skirt side plate',(x,-.13,.74),(.29,.35,.23),'evil_steel','pelvis',.025,(0,x*.30,0))


def flaming_staff():
    g.target(c.PROP_COLLECTION); root=g.empty('evil_staff')
    g.tube('Twisted dark staff shaft',[(0,0,-.83),(.02,0,.23),(.09,0,.69)],[.055,.065,.10],'wood_dark',8)
    for z in [-.12,0,.12]: g.torus('Staff grip wrap',(0,0,z),.067,.02,'leather_light',sides=10)
    g.torus('Iron staff crown',(.08,0,.91),.22,.047,'evil_steel','Y',8)
    for s in [-1,1]:
        g.tube('Staff crooked claw',[(.08+s*.16,0,.71),(.08+s*.29,0,.99),(.08+s*.26,0,1.23),(.08+s*.34,0,1.35)],[.07,.07,.045,.008],'evil_steel',7)
    flame((.08,0,.94),.87)
    g.attach_all(c.PROP_COLLECTION,root)
    return root


def flame(pos=(0,0,0),scale=1):
    x,y,z=pos
    g.lathe('Red magical flame',[(0,.12*scale),(.17*scale,.16*scale),(.32*scale,.08*scale),(.53*scale,0)],'ember',7,pos)
    g.lathe('Bright flame heart',[(0,.078*scale),(.18*scale,.07*scale),(.30*scale,0)],'fire_core',7,(x,y-.095*scale,z-.025*scale))
    for s in [-1,1]:
        g.tube('Curling flame tongue',[(x+s*.08*scale,y,z+.08*scale),(x+s*.17*scale,y,z+.30*scale),(x+s*.12*scale,y,z+.43*scale)],
               [.06*scale,.04*scale,.002],'ember',6)


def hand_flame():
    g.target(c.PROP_COLLECTION); root=g.empty('evil_hand_flame')
    flame((0,0,.14),.65)
    g.attach_all(c.PROP_COLLECTION,root)
    return root


def crossbow():
    g.target(c.PROP_COLLECTION); root=g.empty('crossbow')
    g.cube('Crossbow wooden stock',(.07,0,0),(.94,.14,.16),'wood_light',.035)
    g.cube('Crossbow rear stock',(-.39,0,-.05),(.21,.20,.24),'wood',.03)
    g.beam('Crossbow pistol grip',(-.11,0,-.02),(-.20,0,-.24),.10,.12,'wood_dark')
    points=[(.38,0,-.53),(.55,0,-.37),(.60,0,-.15),(.62,0,0),(.60,0,.15),(.55,0,.37),(.38,0,.53)]
    g.tube('Crossbow curved bow limbs',points,[.039,.043,.05,.058,.05,.043,.039],'wood',8)
    g.tube('Taut crossbow string',[points[0],(-.18,0,.075),points[-1]],.011,'rope',6)
    for x in [-.10,.18,.43]: g.cube('Crossbow iron stock band',(x,0,0),(.045,.16,.175),'evil_edge',.009)
    g.tube('Loaded crossbow bolt',[(-.30,0,.12),(.79,0,.12)],.019,'wood_edge',6)
    g.mesh('Crossbow bolt point',[(.74,-.055,.12),(.74,.055,.12),(.92,0,.12),(.78,0,.17),(.78,0,.07)],[(0,2,3),(3,2,1),(1,2,4),(4,2,0),(0,3,1,4)],'silver_light')
    g.attach_all(c.PROP_COLLECTION,root)
    return root


def evil_axe(name):
    g.target(c.PROP_COLLECTION); root=kit.place('axe'); root.name=name
    recolor(root.children,{'silver':'evil_edge','silver_dark':'evil_steel','silver_light':'silver','wood_light':'wood_dark'})
    stain=g.mesh('Crimson axe blade motif',[(.18,-.061,.64),(.31,-.061,.67),(.47,-.061,.61),(.45,-.061,.44),(.37,-.061,.42),(.32,-.061,.56),(.22,-.061,.49)],[(0,1,2,3,4,5,6)],'evil_red')
    stain.parent=root
    return root


def build(name,asset,props):
    global ATTACHMENTS
    ATTACHMENTS=[]; c.WEIGHTS=[]; c.PROP_COLLECTION=props
    kind={'evil_melee_unit':'melee','evil_mage_unit':'mage','evil_ranged_unit':'ranged','evil_berserker_unit':'berserker'}[name]
    g.target(asset); base_body(kind)
    if kind=='berserker':
        for obj,bone in c.WEIGHTS:
            if obj.name.startswith(('Tapered tunic','Rounded tunic shoulder','Upper sleeve','Forearm sleeve','Chibi glove','Glove thumb')):
                recolor([obj],{slot.material.name.split('.')[0]:'skin' for slot in obj.material_slots if slot.material})
        c.ball('Bare barbarian chest',(0,-.24,1.30),(.35,.095,.22),'skin','spine',3)
        c.weighted(g.mesh('Crimson shoulder tattoo',[(-.35,-.247,1.52),(-.54,-.247,1.47),(-.56,-.247,1.37),(-.47,-.247,1.42),(-.46,-.247,1.35),(-.37,-.247,1.43)],[(0,1,2,3,4,5)],'evil_red'),'upper_arm.R')
        helmet(True); armor(True)
        attached_part('skull',(0,-.32,.81),.35,'pelvis')
    elif kind=='melee': helmet(); armor()
    else:
        c.hood('evil_purple'); c.cape('evil_red')
        if kind=='mage':
            horns(2.42); c.sash('mage'); attached_part('skull',(0,-.32,.81),.35,'pelvis')
        else: c.quiver(); armor()
    ragged_panel()
    spread=.075 if kind=='berserker' else .025
    for obj,bone in c.WEIGHTS:
        if bone.startswith(('thigh.','shin.','foot.')):
            obj.data.transform(Matrix.Translation(Vector((spread if bone.endswith('.L') else -spread,0,0))))
    rig=c.create_rig(asset,leg_spread=spread)
    for root,bone,pos,rotation in ATTACHMENTS: c.equip(root,rig,bone,pos,rotation)
    if kind=='melee':
        sword=c.sword(); sword.name='evil_sword'
        recolor(sword.children,{'silver_light':'evil_edge','gold':'gold','wood_dark':'black'})
        c.equip(sword,rig,'weapon_socket.R',(-.80,-.13,.885),(0,-.25,0))
        shield=c.shield(); shield.name='evil_shield'
        recolor(shield.children,{'blue':'evil_steel','gold':'evil_edge','gold_light':'evil_red'})
        for obj in shield.children:
            if obj.name.startswith('Shield gold heraldry'): obj.name='Crimson shield emblem'
        c.equip(shield,rig,'weapon_socket.L',(.79,-.29,1.08),(0,-.08,0))
        c.define_arm_stance(rig,{'R':((-.24,-.05,-.22),(-.17,-.08,.13))})
        animation='knight'
    elif kind=='mage':
        staff=flaming_staff(); c.equip(staff,rig,'weapon_socket.L',(.85,-.14,.90),(0,.08,0))
        fire=hand_flame(); c.equip(fire,rig,'weapon_socket.R',(-.80,-.13,.885))
        c.define_arm_stance(rig,{'R':((-.28,-.10,-.12),(-.14,-.17,.14))})
        animation='mage'
    elif kind=='ranged':
        weapon=crossbow(); c.equip(weapon,rig,'weapon_socket.L',(.82,-.17,.97))
        c.define_arm_stance(rig,{'L':((.13,-.18,-.22),(-.12,-.24,0)),
                                'R':((.07,-.21,-.18),(.24,-.13,.01))})
        animation='crossbow'
    else:
        for side,s in [('L',1),('R',-1)]:
            axe=evil_axe('evil_axe' if side=='R' else 'evil_axe_offhand')
            c.equip(axe,rig,'weapon_socket.'+side,(s*.80,-.13,.885),(0,s*.17,0 if s>0 else math.pi))
        c.define_arm_stance(rig,{'R':((-.29,-.05,-.20),(-.17,-.05,.07)),
                                'L':((.29,-.05,-.20),(.17,-.05,.07))})
        animation='berserker'
    c.animate(rig,animation); c.pose(rig,animation,'idle',0)
    rig['shared_skeleton']='chibi_v1'; rig['forward']='-Y'; rig['modeling_stage']='initial_model'
    rig['animation_notes']='Six starter clips at 24fps. Idle/walk/run loop; in-place locomotion.'
    return rig
