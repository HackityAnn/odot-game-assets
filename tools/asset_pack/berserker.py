"""Bare-chested, fur-trimmed dual-axe costume on the shared chibi skeleton."""
import math
import bpy
from mathutils import Matrix, Vector
import geometry as g
import characters as c
import village_kit as kit


def fur_strip(points,bone,radius=.08):
    for i,p in enumerate(points):
        c.ball('Shaggy cream fur tuft',p,(radius*.83,radius*.68,radius*(1.1 if i%2 else 1.35)),'fur',bone,1)


def build(asset,props):
    c.WEIGHTS=[]; c.PROP_COLLECTION=props
    g.target(asset); c.body('knight')
    # Reuse the body and all 19 joint positions; replace the tunic and gloves by skin.
    for obj,bone in list(c.WEIGHTS):
        if obj.name.startswith(('Tunic skirt','Tunic gold','Gold belt buckle','Buckle opening','Buckle tongue')):
            c.WEIGHTS.remove((obj,bone)); bpy.data.objects.remove(obj,do_unlink=True)
        elif obj.name.startswith(('Tapered tunic','Rounded tunic shoulder','Upper sleeve','Forearm sleeve','Chibi glove','Glove thumb')):
            obj.data.materials.clear(); obj.data.materials.append(g.M['skin'])
            if obj.name.startswith('Tapered tunic'):
                obj.name='Broad bare torso'
                for v in obj.data.vertices: v.co.x*=1.12
    for s in [-1,1]:
        c.ball('Rounded chest muscle',(s*.205,-.245,1.34),(.225,.075,.14),'skin','spine',3)
        side='L' if s>0 else 'R'
        c.ball('Berserker upper arm muscle',(s*.49,-.045,1.33),(.21,.19,.23),'skin','upper_arm.'+side,2)
        for y in [-.15,.04,.19]:
            fur_strip([(s*(.22+i*.069),y,1.64-i*.033) for i in range(7)],'upper_arm.'+side,.105)
        c.limb('Leather forearm bracer',(s*.66,-.04,1.08),(s*.78,-.085,.92),[.145,.145],'leather','forearm.'+side)
        fur_strip([(s*.74+math.cos(a)*.15,-.08+math.sin(a)*.15,1.05) for a in [i*math.tau/8 for i in range(8)]],'forearm.'+side,.072)
        fur_strip([(s*.235+math.cos(a)*.14,-.025+math.sin(a)*.14,.36) for a in [i*math.tau/8 for i in range(8)]],'shin.'+side,.065)
        # Lower the brow toward the nose for the determined reference expression.
        c.part('Angled orange eyebrow',(s*.15,-.414,2.174),(.22,.027,.056),'hair','head',.014,(0,-s*.17,0))
        for i in range(3):
            c.ball('Swept side beard',(s*(.27-i*.028),-.30-i*.041,1.93-i*.091),(.15,.115,.15),'hair','head',2)
        c.limb('Sweeping moustache',(s*.035,-.432,1.975),(s*.26,-.43,1.91),[.07,.025],'hair_light','head')
    c.ball('Nose',(0,-.427,2.0),(.065,.075,.073),'skin','head',2)
    beard=c.weighted(g.lathe('Faceted tapered orange beard',[(1.53,.025),(1.69,.19),(1.89,.28),(2.0,.20)],'hair',12,center=(0,-.32,0)),'head')
    for v in beard.data.vertices: v.co.y=-.32+(v.co.y+.32)*.65
    for s in [-1,0,1]:
        c.ball('Pointed front beard lock',(s*.09,-.43,1.76),(.085,.073,.18),'hair_light' if s==0 else 'hair','head',2)
    hair=c.weighted(g.lathe('Orange swept hair crown',[(2.24,.405),(2.37,.435),(2.49,.32),(2.56,0)],'hair',16),'head')
    for v in hair.data.vertices: v.co.y*=.95
    for i in range(5):
        x=(i-2)*.125
        c.ball('Swept forehead hair lock',(x,-.235,2.42),(.095,.20,.125),'hair_light' if i%2 else 'hair','head',2)
        c.weighted(g.tube('Carved flowing hair groove',[(x,-.37,2.30),(x-.02,-.25,2.50),(x-.07,-.06,2.52)],[.012,.014,.002],'hair_light',6),'head')
    c.weighted(g.torus('Topknot leather tie',(0,.30,2.52),.13,.03,'leather',sides=12),'head')
    for pos,size in [((0,.34,2.61),(.14,.15,.16)),((-.10,.36,2.83),(.23,.22,.28)),
                     ((-.27,.25,3.00),(.23,.19,.18)),((-.44,.19,3.04),(.15,.12,.10))]:
        c.ball('High swept ponytail lock',pos,size,'hair','head',2)
    c.weighted(g.tube('Ponytail tapered tip',[(-.43,.18,3.04),(-.62,.15,3.01)],[.09,.008],'hair',8),'head')
    c.weighted(g.beam('Leather diagonal chest strap',(-.30,-.31,1.49),(.25,-.29,1.04),.12,.048,'leather',.015),'spine')
    for t in [.2,.43,.66,.86]: c.ball('Chest strap silver rivet',(-.30+.55*t,-.341,1.49-.45*t),(.020,.012,.020),'silver','spine',1)
    c.part('Wide berserker belt',(0,-.01,.94),(.75,.49,.15),'leather','pelvis',.03)
    c.weighted(g.torus('Round silver belt buckle',(0,-.28,.95),.108,.033,'silver_light','Y',16),'pelvis')
    c.weighted(g.beam('Buckle pin',(-.04,-.32,.95),(.08,-.32,.95),.025,.025,'silver'),'pelvis')
    for x in [-.27,-.15,.15,.27]: c.ball('Belt iron rivet',(x,-.27,.945),(.025,.018,.025),'silver','pelvis',1)
    c.weighted(g.mesh('Ragged blue loincloth',[(-.26,-.30,.88),(.26,-.30,.88),(.23,-.33,.51),(.10,-.34,.55),(0,-.34,.45),(-.12,-.34,.55),(-.24,-.33,.51)],[(0,1,2,3,4,5,6)],'blue'),'pelvis')
    fur_strip([(-.25+i*.063,-.32,.88) for i in range(9)],'pelvis',.055)
    for s in [-1,1]:
        fur_strip([(s*(.12+i*.10),-.18,.82-i*.025) for i in range(4)],'pelvis',.068)
    for obj,bone in c.WEIGHTS:
        if bone.startswith(('thigh.','shin.','foot.')):
            side=1 if bone.endswith('.L') else -1
            obj.data.transform(Matrix.Translation(Vector((side*.105,0,0))))
    rig=c.create_rig(asset,leg_spread=.105)
    g.target(props)
    right=kit.place('axe'); right.name='axe'
    left=kit.place('axe'); left.name='axe_offhand'
    c.equip(right,rig,'weapon_socket.R',(-.80,-.13,.885),(0,-.20,math.pi))
    c.equip(left,rig,'weapon_socket.L',(.80,-.13,.885),(0,.20,0))
    c.define_arm_stance(rig,{'R':((-.30,-.04,-.18),(-.20,-.06,.14)),
                            'L':((.29,-.02,-.19),(.20,-.04,-.16))})
    c.animate(rig,'berserker')
    c.pose(rig,'berserker','idle',0)
    rig['shared_skeleton']='chibi_v1'
    rig['animation_notes']='Six starter clips at 24fps, dual-axe attack; idle/walk/run loop.'
    rig['forward']='-Y'
    return rig
