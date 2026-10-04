"""Seven buildings authored from the separate autobattler reference images."""
import math
from mathutils import Vector
import geometry as g
import buildings as cottage
import village_kit as kit


def group(name, builder, pos=(0,0,0), scale=1, rotation=(0,0,0)):
    previous=set(g.CURRENT.objects)
    builder()
    objects=set(g.CURRENT.objects)-previous
    root=g.empty(name,pos); root.rotation_euler=rotation
    root.scale=(scale,)*3 if isinstance(scale,(int,float)) else scale
    for obj in objects:
        if obj.parent is None: obj.parent=root
    return root


def masonry(width=1.75, depth=1.60, height=2.0, pos=(0,0,0)):
    x,y,z=pos
    core=g.cube('Mortared stone tower core',(x,y,z+height/2),(width-.045,depth-.045,height),'stone_light',.035)
    core['wall_surface']=True
    rows=max(1,round(height/.42))
    for row in range(rows):
        bottom=z+row*height/rows
        for side in [-1,1]:
            for left,right in courses(width,max(2,round(width/.48)),row):
                xx=x+(left+right)/2
                block=kit.place('stone_block',(xx,y+side*(depth/2-.035),bottom),
                          ((right-left-.022)/.43,.65,height/rows/.28*.95))
                for obj in block.children: obj['wall_surface']=True
            for left,right in courses(depth,max(2,round(depth/.48)),row):
                yy=y+(left+right)/2
                kit.place('stone_block',(x+side*(width/2-.035),yy,bottom),
                          ((right-left-.022)/.43,.65,height/rows/.28*.95),(0,0,math.pi/2))
    g.cube('Projecting tower foundation',(x,y,z+.12),(width+.20,depth+.20,.24),'wall_light',.045)


def courses(length,count,row):
    joints=[-length/2]+[-length/2+(i+(0.5 if row%2 else 1))*length/count
                         for i in range(count)]+[length/2]
    joints=sorted(set(v for v in joints if -length/2<=v<=length/2))
    return list(zip(joints,joints[1:]))


def stone_arch(x,y,z,width,height,mat='wall_light'):
    r=width/2+.065; spring=z+height-width/2
    for sign in [-1,1]:
        for i in range(max(1,round((spring-z)/.26))):
            h=(spring-z)/max(1,round((spring-z)/.26))
            g.cube('Door jamb stone',(x+sign*(r+.075),y,z+(i+.5)*h),(.20,.28,h-.018),mat,.035)
    for i in range(9):
        a=i*math.pi/9; b=(i+1)*math.pi/9-.035
        pts=[(x+rr*math.cos(t),yy,spring+rr*math.sin(t))
             for yy in [y-.14,y+.13] for rr,t in [(r,a),(r,b),(r+.20,b),(r+.20,a)]]
        g.mesh('Arched keystone course',pts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,.017)


def bolt(pos,radius=.025):
    g.tube('Round iron joinery rivet',[pos,(pos[0],pos[1]-.012,pos[2])],radius,'silver_dark',10)


def timber_finish():
    # Grain follows each timber's baked local geometry; no textures are needed.
    for obj in list(g.CURRENT.objects):
        if obj.type!='MESH' or obj.parent is not None: continue
        if not obj.name.startswith(('Corner upright','Lookout upright','Banner post','Hoist upright','Trade sign post','Canopy upright')): continue
        verts=[v.co for v in obj.data.vertices]
        x0,x1=min(v.x for v in verts),max(v.x for v in verts)
        y=min(v.y for v in verts)-.006
        z0,z1=min(v.z for v in verts),max(v.z for v in verts)
        for offset in [-.2,.16]:
            x=(x0+x1)/2+(x1-x0)*offset
            g.tube('Carved timber grain',[(x,y,z0+.15),(x+.013,y,(z0+z1)/2),(x-.005,y,z1-.12)],.005,'wood_dark',4)
        for z in [z0+.20,z1-.20]: bolt(((x0+x1)/2,y-.005,z))


def wooden_stairs(x,y,height=.36,steps=3,width=.66):
    for i in range(steps):
        g.cube('Wooden entrance stair tread',(x,y+i*.21,height*(i+1)/steps),(width,.255,.08),'wood_light',.018)
    for s in [-1,1]:
        g.beam('Wooden stair stringer',(x+s*width*.47,y-.14,.055),(x+s*width*.47,y+(steps-1)*.21+.10,height+.10),.10,.12,'wood_edge')


def stairs(x,y,height=.35,steps=3,width=.80):
    for i in range(steps):
        h=height*(i+1)/steps
        g.cube('Limestone entrance step',(x,y+i*.23,h/2),(width,.26,h),'wall_light',.035)


def glyph(kind,x,y,z,size=.45,mat='cream'):
    if kind in ['arrow','sword']:
        g.beam('Heraldic shaft',(x,y,z-size*.35),(x,y,z+size*.30),size*.15,.06,mat,.008)
        cottage.relief('Heraldic pointed blade',[(x-size*.17,z+size*.15),(x+size*.17,z+size*.15),(x,z+size*.52)],y-.035,.07,mat)
        if kind=='sword': g.cube('Heraldic crossguard',(x,y-.015,z-size*.10),(size*.62,.07,size*.13),mat,.012)
        else:
            for s in [-1,1]: g.beam('Arrow fletching',(x,y,z-size*.2),(x+s*size*.22,y,z-size*.43),size*.07,.025,mat,.004)
    elif kind=='rook':
        g.cube('Rook emblem',(x,y,z-size*.04),(size*.44,.026,size*.54),mat,.007)
        for dx in [-.21,0,.21]: g.cube('Rook battlement',(x+dx*size,y,z+size*.28),(size*.16,.027,size*.19),mat,.003)
        g.cube('Rook foot',(x,y,z-size*.34),(size*.65,.027,size*.09),mat,.004)
    elif kind=='eye':
        cottage.relief('Arcane diamond',[(x-size*.42,z),(x,z+size*.42),(x+size*.42,z),(x,z-size*.42)],y-.03,.065,mat)
        g.tube('Eye pupil',[(x,y-.04,z),(x,y-.10,z)],size*.14,'purple_dark',12)


def banner(pos,kind='arrow',width=.53,height=.98,mat='blue'):
    x,y,z=pos
    points=[(x-width/2,y,z),(x+width/2,y,z),(x+width/2,y-.03,z-height*.78),
            (x+width*.18,y-.01,z-height),(x,y+.01,z-height*.80),
            (x-width*.18,y-.025,z-height),(x-width/2,y,z-height*.78)]
    ob=g.mesh('Cloth heraldic banner',points,[tuple(range(7))],mat)
    modifier=ob.modifiers.new('Cloth thickness','SOLIDIFY'); modifier.thickness=.045
    for s in [-1,1]: g.beam('Gold banner border',(x+s*width*.44,y-.022,z-.05),(x+s*width*.44,y-.045,z-height*.75),.018,.018,'gold',.004)
    g.beam('Banner hanging rod',(x-width*.63,y,z+.055),(x+width*.63,y,z+.055),.05,.05,'wood_edge')
    glyph(kind,x,y-.08,z-height*.45,width*.90)


def hip_roof(z=3.75,radius=1.18,rise=1.02):
    peak=z+rise
    for side in range(4):
        angle=side*math.pi/2
        def make_side():
            for row in range(3):
                bottom=radius*(1-row/3)+.04
                top=max(.035,radius*(1-(row+1)/3)+.04)
                low=z+rise*row/3; high=z+rise*(row+1)/3
                count=max(2,round(bottom*2/.50))
                for col in range(count):
                    a=col/count; b=(col+1)/count
                    face=[(-bottom+2*bottom*a+.008,-bottom,low),
                          (-bottom+2*bottom*b-.008,-bottom,low),
                          (-top+2*top*b-.005,-top,high),
                          (-top+2*top*a+.005,-top,high)]
                    verts=face+[(x,y,zz-.095) for x,y,zz in face]
                    g.mesh('Tapered solid hip roof shingle',verts,
                           [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],
                           g.RNG.choice(['roof_blue','roof_blue','roof_blue_light']),.02)
            g.beam('Roof eave beam',(-radius-.09,-radius-.02,z),(radius+.09,-radius-.02,z),.14,.14,'wood_light')
            g.beam('Hip ridge beam',(-radius,-radius,z+.035),(0,0,peak+.02),.11,.11,'wood_edge')
        group('Hip roof quadrant',make_side,rotation=(0,0,angle))
    g.cube('Roof chunky finial',(0,0,peak+.11),(.28,.28,.22),'wood_edge',.04)


def ladder(a,b,width=.42,rungs=8):
    a,b=Vector(a),Vector(b)
    for s in [-1,1]:
        offset=Vector((s*width/2,0,0))
        g.beam('Ladder rail',a+offset,b+offset,.07,.075,'wood_light')
    for i in range(rungs):
        p=a+(b-a)*(i+.35)/rungs
        g.beam('Ladder rung',p+Vector((-width/2,0,0)),p+Vector((width/2,0,0)),.06,.06,'wood_edge')


def lantern_arm(pos):
    x,y,z=pos
    g.beam('Lantern bracket',(x,y+.25,z+.32),(x,y-.12,z+.32),.09,.09,'wood_light')
    g.tube('Lantern chain',[(x,y-.10,z+.32),(x,y-.10,z+.18)],.014,'iron',6)
    kit.place('lantern',(x,y-.10,z-.08),.90)


def front_path():
    for x,y,s in [(-.14,-1.27,.26),(.05,-1.72,.30),(.40,-2.02,.26)]: g.stepping_stone((x,y),s)


def dress():
    for pos,s in [((-1.4,.7,0),1.05),((1.45,.85,0),1.0),((1.75,-.65,0),.75),((-.75,-1.98,0),.5)]: kit.place('shrub',pos,s)
    g.fence((-1.9,.30,0),(-1.9,1.3,0),3,.48)
    g.fence((1.85,.45,0),(1.85,1.35,0),3,.48)
    timber_finish()


def arrow_tower():
    masonry(1.55,1.48,2.02)
    cottage.door(.14,-.79,.22,.54,1.17); stairs(.14,-1.20,.24,2,.66)
    stone_arch(.14,-.80,.22,.54,1.17,'wood_edge')
    for i in range(8): g.cube('Upper lookout deck plank',(-.98+i*.28,0,2.11),(.27,2.08,.14),'wood_light',.018)
    for x in [-1,1]:
        for y in [-1,1]:
            g.cube('Lookout upright',(x,y,2.93),(.28,.28,1.72),'wood_light',.035)
            g.cube('Rail post cap',(x,y,2.79),(.36,.36,.18),'wood_edge',.025)
            g.beam('Deck knee brace',(x*.68,y*.64,1.53),(x,y,2.10),.22,.22,'wood')
            g.ico('Joinery iron bolt',(x,y-.09,2.72),(.035,.018,.035),'iron',1)
    for y in [-1,1]:
        for z in [2.31,2.68]: g.beam('Lookout railing',(-1.08,y,z),(1.08,y,z),.10,.12,'wood_edge')
    for x in [-1,1]:
        for z in [2.31,2.68]: g.beam('Lookout railing',(x,-1,z),(x,1,z),.10,.12,'wood_edge')
    for z in [2.33,2.52]:
        g.cube('Lookout front parapet plank',(0,-1.01,z),(2.02,.11,.17),'wood_light',.025)
        g.cube('Lookout rear parapet plank',(0,1.01,z),(2.02,.11,.17),'wood_light',.025)
        for s in [-1,1]: g.cube('Lookout side parapet plank',(s*1.01,0,z),(.11,2.02,.17),'wood_light',.025)
    hip_roof(3.65,1.21,1.03)
    ladder((-.90,-1.64,.04),(-.90,-.79,2.14),.38,9)
    banner((.36,-1.15,2.72),'arrow',.85,1.25)
    lantern_arm((-1.12,-1.20,2.93))
    kit.place('target',(1.37,-1.15,0),1.32,(0,0,-.10))
    kit.place('open_barrel',(-1.27,-1.15,0),.92)
    for i in range(5): kit.place('arrow',(-1.27+(i%3-1)*.07,-1.15+(i//3)*.08,1.12),.92,(math.pi,(i-2)*.08,0))
    kit.place('open_crate',(.64,-.03,2.20),.92)
    for i in range(3): kit.place('arrow',(.55+i*.10,-.02,2.49),1.48,(0,(i-1)*.13,0))
    dress(); front_path()


def cannon():
    # Barrel has a real hollow muzzle; the dark inner cap sits deep inside it.
    a=Vector((-.65,-.04,3.20)); b=Vector((1.17,-.28,3.93)); direction=(b-a).normalized()
    g.tube('Iron cannon barrel',[a,b],[.36,.43],'iron',16,caps=False)
    g.ico('Cannon breech',a,(.36,.36,.36),'iron',2,.01)
    g.tube('Muzzle bore',[b-direction*.36,b],[.315,.35],'black',16,caps=False)
    g.tube('Recessed bore bottom',[b-direction*.365,b-direction*.36],.315,'black',16)
    for t in [.12,.50,.92,1]:
        p=a.lerp(b,t)
        # Closed annular muzzle rim, retaining a visible bore at all angles.
        outer=.46 if t>.9 else .40
        g.tube('Cannon reinforcing ring',[p-direction*.055,p+direction*.055],outer,'silver_dark',16,caps=False)
        if t==1:
            end=p+direction*.055
            rot=direction.to_track_quat('Z','Y').to_matrix()
            verts=[end+rot @ Vector((r*math.cos(i*math.tau/16),r*math.sin(i*math.tau/16),0)) for r in [outer,.35] for i in range(16)]
            g.mesh('Thick annular cannon muzzle',verts,[(i,(i+1)%16,(i+1)%16+16,i+16) for i in range(16)],'silver_dark')
    g.cube('Gun carriage bed',(-.20,0,2.84),(1.35,.86,.24),'wood_light',.04)
    for y in [-.46,.46]:
        cottage.relief('Gun carriage cheek',[(-.76,2.78),(.35,2.78),(.18,3.18),(-.56,3.23)],y,.14,'wood',.035)
        for x in [-.60,.22]:
            g.tube('Cannon wooden wheel',[(x,y-.065,2.77),(x,y+.065,2.77)],.29,'wood_light',12)
            g.torus('Wheel iron tire',(x,y,2.77),.285,.035,'iron','Y',12)
            g.tube('Wheel hub',[(x,y-.08,2.71),(x,y+.08,2.71)],.064,'silver_dark',10)
    g.tube('Cannon trunnion',[(a.x+.48,-.45,3.29),(a.x+.48,.45,3.29)],.08,'silver_dark',10)


def bombarding_tower():
    masonry(1.83,1.65,2.36)
    for i in range(9): g.cube('Gun platform plank',(-1.02+i*.255,0,2.45),(.245,2.18,.17),'wood_light')
    for x in [-1,1]:
        for y in [-.97,.97]:
            g.cube('Platform upright',(x,y,1.82),(.15,.15,1.48),'wood_light')
            g.beam('Gun deck brace',(x*.70,y*.66,1.72),(x,y,2.46),.13,.13,'wood')
    for s in [-1,1]:
        g.cube('Battlement base course',(0,s*1.0,2.64),(2.17,.23,.22),'wall_light',.029)
        g.cube('Battlement base course',(s*1.03,0,2.64),(.23,1.98,.22),'wall_light',.029)
        for i in range(4):
            g.cube('Stone crenellation',(-.84+i*.56,s*1.00,2.76),(.37,.24,.38),'wall_light',.035)
            g.cube('Stone crenellation',(s*1.03,-.63+i*.42,2.76),(.24,.28,.38),'wall_light',.025)
    cannon(); banner((.47,-1.20,2.52),'rook',.83,1.17)
    cottage.window(-.49,-.895,.74,.45,.73)
    stone_arch(-.49,-.89,.74,.45,.73,'wood_edge')
    cottage.door(.46,-.87,.35,.48,1.17)
    wooden_stairs(.52,-1.48,.35,3,.60)
    stone_arch(.46,-.89,.35,.48,1.17)
    lantern_arm((1.04,-.89,1.92))
    kit.place('open_crate',(-1.27,-.84,0),1.05)
    for x,y in [(-1.36,-.86),(-1.19,-.86),(-1.28,-.70)]: kit.place('cannonball',(x,y,.45),.80)
    for x,y,z in [(-1.50,-1.45,0),(-1.25,-1.45,0),(-1.38,-1.20,0),(-1.38,-1.36,.20)]: kit.place('cannonball',(x,y,z),1)
    kit.place('barrel',(1.40,.15,0),.84); kit.place('barrel',(1.43,.77,0),.75)
    dress()


def cottage_shell(stone=True):
    cottage.cottage_body(stone=stone)
    # The same tile mesh is shared across every cottage and the tower roofs.
    peak=3.21; slope=.82; angle=math.atan(slope)
    for sign in [-1,1]:
        g.cube('Roof timber underlay',(sign*.64,0,peak-.64*slope),(1.75,2.25,.13),'wood_dark',.02,(0,sign*angle,0))
        for row in range(4):
            x=sign*(.16+row*.35)
            for col in range(5):
                y=-.92+col*.46+(row%2)*.035
                kit.place('roof_tile',(x,y,peak-abs(x)*slope+.07),(1.42,1.42,1.75),(0,sign*angle,0))
        for y in [-1.18,1.18]: g.beam('Carved roof verge',(0,y,peak+.05),(sign*1.48,y,peak-1.48*slope),.25,.24,'wood_light')
        g.beam('Roof eave',(sign*1.43,-1.16,2.02),(sign*1.43,1.16,2.02),.13,.17,'wood_dark')
    g.beam('Ridge timber',(0,-1.32,3.32),(0,1.35,3.32),.19,.21,'wood_light')
    for y in [-1.14,.05,1.10]: g.cube('Ridge peg',(0,y,3.39),(.25,.20,.26),'wood_edge',.022)


def dormer(pos=(.77,.23,2.45)):
    def make():
        g.cube('Dormer body',(0,0,.28),(.52,.48,.56),'wood')
        g.mesh('Dormer gable',[(-.26,-.255,.52),(.26,-.255,.52),(0,-.255,.85)],[(0,1,2)],'wood_light')
        cottage.window(0,-.27,.13,.28,.45)
        for s in [-1,1]:
            for row in range(2):
                kit.place('roof_tile',(s*(.11+row*.17),0,.85-(.11+row*.17)*.95),(.60,1.75,1),(0,s*.76,0))
    group('Glowing roof dormer',make,pos,scale=1.25,rotation=(0,0,math.pi/2))


def shield_emblem(pos=(0,-1.17,2.56),size=1.02,kind='sword'):
    x,y,z=pos
    outline=[(-.43,.45),(.43,.45),(.44,-.10),(.24,-.40),(0,-.59),(-.24,-.40),(-.44,-.10)]
    for factor,dy,mat in [(1,0,'gold'),(.84,-.03,'blue')]:
        cottage.relief('Barracks heraldic shield',[(x+xx*size*factor,z+zz*size*factor) for xx,zz in reversed(outline)],y+dy,.09,mat,.025)
    glyph(kind,x,y-.10,z,size*.82)


def barracks():
    cottage_shell()
    cottage.portal(-.15,-.95,.23,.69,1.42)
    cottage.arch('Open barracks doorway',-.15,-.65,.23,.69,1.42,'shadow')
    g.cube('Barracks interior lamp',(-.37,-.70,.74),(.18,.06,.64),'window',.02)
    g.cube('Barracks inner timber',(.04,-.74,.81),(.07,.07,1.09),'wood_light',.01)
    stairs(-.15,-1.48,.27,3,.86); shield_emblem()
    stone_arch(-.15,-.98,.23,.69,1.42)
    # A visible interior threshold gives the doorway depth in the presentation view.
    for z in [.38,.51]: g.cube('Barracks inner step',(-.15,-.992,z),(.48,.015,.04),'wood_edge',.006)
    masonry(.52,.52,3.53,(-.67,.51,0))
    g.cube('Barracks tower cap',(-.67,.51,3.59),(.72,.72,.16),'wood_light')
    g.beam('Flag pole',(-.67,.51,3.65),(-.67,.51,4.21),.045,.045,'wood_light')
    g.mesh('Barracks blue flag',[(-.67,.51,4.21),(-.12,.49,4.13),(-.26,.52,3.87),(-.67,.51,3.92)],[(0,1,2,3)],'blue')
    g.cube('Banner post',(1.46,-.31,1.45),(.16,.16,2.90),'wood_light')
    g.beam('Banner crossarm',(.93,-.31,2.82),(1.77,-.31,2.82),.15,.13,'wood_edge')
    banner((1.49,-.54,2.83),'sword',.88,1.36); lantern_arm((1.91,-.34,2.70))
    for z in [.54,1.08]: g.beam('Spear rack cross rail',(-1.62,-.88,z),(-.86,-.88,z),.09,.09,'wood')
    for x in [-1.58,-.9]: g.cube('Spear rack post',(x,-.88,.55),(.08,.08,1.1),'wood_light')
    for i in range(3): kit.place('spear',(-1.52+i*.23,-.99,.12),1.12,(0,-.10,0))
    for r,y,mat in [(.27,-1.06,'gold'),(.23,-1.08,'blue'),(.055,-1.12,'gold')]: g.tube('Rack round shield',[(-1.13,y,.47),(-1.13,y-.018,.47)],r,mat,16)
    g.beam('Dummy post',(1.23,-1.30,0),(1.23,-1.30,1.21),.09,.09)
    g.beam('Dummy crossarm',(.88,-1.30,.91),(1.59,-1.30,.91),.10,.10,'wood_light')
    g.ico('Padded training torso',(1.23,-1.30,.90),(.24,.14,.33),'cream',2,.03)
    g.tube('Dummy bullseye',[(1.23,-1.445,.91),(1.23,-1.46,.91)],.105,'red',16)
    g.ico('Dummy padded head',(1.23,-1.30,1.26),(.12,.11,.15),'cream',2)
    for s in [-1,1]: g.cube('Dummy foot brace',(1.23+s*.15,-1.30,.055),(.36,.13,.11),'wood',.02)
    kit.place('barrel',(1.31,-.62,0),.91); kit.place('crate',(-.99,-1.25,0),.79)
    dress(); front_path()


def canopy(x=0,y=-1.04,z=1.95,width=2.16,depth=.94,striped=False):
    strips=8 if striped else 1
    for i in range(strips):
        left=x-width/2+i*width/strips; right=left+width/strips
        profile=[(y,z),(y-depth*.32,z-.05),(y-depth*.77,z-.31),(y-depth,z-.35),(y-depth-.035,z-.59)]
        verts=[(xx,yy,zz) for xx in [left,right] for yy,zz in profile]
        ob=g.mesh('Canvas canopy stripe' if striped else 'Linen work canopy',verts,[(j,j+1,j+6,j+5) for j in range(4)],'red' if striped and i%2==0 else 'cream')
        mod=ob.modifiers.new('Canvas thickness','SOLIDIFY'); mod.thickness=.018
    for xx in [x-width/2,x+width/2]:
        g.cube('Canopy upright',(xx,y-depth+.04,(z-.28)/2),(.10,.10,z-.28),'wood_light')
        g.beam('Canopy support rib',(xx,y,z-.03),(xx,y-depth,z-.38),.07,.07,'wood')
    g.beam('Awning front beam',(x-width/2-.09,y-depth,z-.36),(x+width/2+.09,y-depth,z-.36),.10,.10,'wood_edge')


def table(pos=(1.18,-1.31,0),width=1.06,depth=.54,height=.70):
    x,y,z=pos
    for i in range(4): g.cube('Table top plank',(x,y+(i-1.5)*depth/4,z+height),(width,depth/4-.008,.10),'wood_light',.02)
    for dx in [-width*.37,width*.37]:
        for dy in [-depth*.29,depth*.29]: g.cube('Table leg',(x+dx,y+dy,z+height/2),(.09,.09,height),'wood',.015)
    g.beam('Table stretcher',(x-width*.38,y,z+.20),(x+width*.38,y,z+.20),.09,.08,'wood_edge')


def sign(pos,kind='beer'):
    return group('Oversized '+kind+' hanging sign',lambda:sign_parts((0,0,0),kind),pos,1.55)


def sign_parts(pos,kind):
    x,y,z=pos
    g.beam('Sign bracket',(x+.33,y,z+.28),(x-.32,y,z+.28),.13,.13,'wood_light')
    for dx in [-.23,.23]: g.tube('Sign iron chain',[(x+dx,y,z+.27),(x+dx,y,z+.02)],.012,'iron',6)
    g.cube('Carved hanging sign',(x,y,z-.15),(.68,.16,.53),'wood_light',.055)
    if kind=='beer':
        g.cube('Foamy mug sign emblem',(x,y-.115,z-.18),(.28,.08,.26),'gold',.025)
        g.torus('Sign mug handle',(x+.17,y-.12,z-.18),.09,.024,'cream','Y',12)
        for dx in [-.09,0,.09]: g.ico('Sign foam',(x+dx,y-.13,z-.045),(.072,.035,.065),'cream',2)
    else:
        g.beam('Scale sign upright',(x,y-.14,z-.29),(x,y-.14,z+.02),.045,.055,'gold',.008)
        g.beam('Scale sign crossarm',(x-.23,y-.14,z-.06),(x+.23,y-.14,z-.06),.045,.055,'gold',.008)
        for s in [-1,1]:
            g.tube('Scale sign rope',[(x+s*.17-.08,y-.145,z-.25),(x+s*.17,y-.145,z-.055),(x+s*.17+.08,y-.145,z-.25)],.014,'gold',6)
            cottage.relief('Scale pan emblem',[(x+s*.17-.095,z-.25),(x+s*.17,z-.32),(x+s*.17+.095,z-.25)],y-.17,.05,'gold',.008)


def tavern():
    cottage_shell(); cottage.chimney(); dormer()
    cottage.door(-.40,-.975,.23,.62,1.44); stairs(-.40,-1.49,.25,3,.81)
    stone_arch(-.40,-1.0,.23,.62,1.44)
    g.torus('Tavern iron door ring',(-.22,-1.08,.92),.081,.019,'iron','Y',16)
    group('Side tavern window',lambda:cottage.window(0,-1.15,.95,.50,.70),rotation=(0,0,math.pi/2))
    for y in [-.43,.43]:
        for i in range(3): g.cube('Tavern wooden shutter',(1.20,y+(i-1)*.065,1.31),(.075,.064,.65),'wood_light',.014)
        for z in [1.08,1.52]: g.cube('Shutter iron strap',(1.245,y,z),(.017,.20,.03),'iron',.005)
    lantern_arm((.09,-1.0,1.70)); sign((-1.60,-1.27,2.47))
    g.beam('Tavern sign cantilever',(-.97,-1.12,2.92),(-2.12,-1.27,2.92),.19,.18,'wood_edge')
    g.beam('Tavern sign diagonal support',(-1.03,-1.12,2.40),(-1.48,-1.22,2.92),.14,.14,'wood_light')
    kit.place('barrel',(-1.48,-1.06,0),.81); kit.place('barrel',(1.56,.31,0),.93)
    table((1.12,-1.38,0),1.06,.54,.69)
    for y in [-1.91,-.94]: kit.place('bench',(1.12,y,0),.92)
    kit.place('mug',(.91,-1.44,.75),2.25); kit.place('mug',(1.32,-1.29,.75),1.55)
    kit.place('lantern',(1.43,-1.47,.95),.64)
    dress(); front_path()


def stone_cutter():
    cottage_shell(); cottage.chimney()
    cottage.portal(0,-.96,.06,1.34,1.80)
    cottage.arch('Workshop shadow opening',0,-.66,.06,1.34,1.80,'shadow')
    g.cube('Workshop recessed floor',(0,-1.00,.09),(1.35,.55,.16),'wood_light',.025)
    canopy(-.20,-1.01,2.0,1.77,.60)
    group('Stone workshop side window',lambda:cottage.window(0,-1.15,1.01,.48,.71),rotation=(0,0,math.pi/2))
    # Grindstone sits vertical on an actual through axle and two trestles.
    for y in [-1.72,-1.05]: g.cube('Grindstone trestle',(-1.42,y,.35),(.48,.10,.70),'wood_light')
    g.tube('Grindstone axle',[(-1.42,-1.85,.73),(-1.42,-.93,.73)],.065,'iron',10)
    g.tube('Circular grindstone',[(-1.36,-1.65,.83),(-1.36,-1.29,.83)],.55,'stone',16)
    g.torus('Grinding wheel rim',(-1.36,-1.66,.83),.49,.04,'stone_light','Y',16)
    g.tube('Grindstone raised hub',[(-1.36,-1.66,.83),(-1.36,-1.74,.83)],.11,'iron',12)
    g.tube('Crank axle',[(-1.42,-1.85,.73),(-1.42,-1.92,.73),(-1.42,-1.92,.93),(-1.62,-1.92,.93)],.028,'iron',8)
    table((1.03,-1.57,0),1.13,.62,.74)
    for x,y,s in [(.77,-1.60,.81),(1.02,-1.48,.66),(1.36,-1.58,.51)]: kit.place('stone_block',(x,y,.79),s)
    g.beam('Stone hammer handle',(1.10,-1.66,.80),(1.44,-1.81,.91),.045,.045,'wood_edge')
    g.cube('Stone hammer head',(1.13,-1.67,.89),(.16,.095,.15),'iron',.02)
    g.beam('Steel chisel',(.66,-1.77,.80),(.86,-1.70,1.10),.031,.031,'silver',.003)
    g.cube('Hoist upright',(-1.60,-.52,1.34),(.20,.20,2.68),'wood_light')
    g.beam('Hoist jib',(-1.53,-.52,2.62),(-2.05,-.99,2.62),.18,.18,'wood_edge')
    g.beam('Hoist brace',(-1.60,-.52,2.04),(-1.95,-.90,2.62),.11,.11,'wood')
    g.tube('Hoist rope',[(-2.02,-.97,2.65),(-2.02,-.97,1.68)],.029,'rope',8)
    g.torus('Hoist iron hook',(-2.02,-.97,1.73),.07,.022,'iron','Y',12)
    kit.place('stone_block',(-1.99,-.97,1.15),(1.75,1.75,1.50))
    for dx in [-.30,.30]: g.tube('Block lifting sling',[(-1.99,-.97,1.78),(-1.99+dx,-1.25,1.54),(-1.99+dx,-1.25,1.15),(-1.99+dx,-.69,1.15),(-1.99,-.97,1.78)],.037,'rope',6)
    for x,y in [(-1.64,-.73),(1.57,.27)]:
        for j in range(3): g.cube('Stone pallet slat',(x+(j-1)*.17,y,.06),(.15,.61,.10),'wood_light')
        for row in range(2):
            for i in range(2): kit.place('stone_block',(x+(i-.5)*.23,y,.11+row*.18),.72)
    kit.place('open_barrel',(.67,-1.94,0),.68)
    for i in range(5): g.ico('Barrel stone offcut',(.67+(i%3-1)*.075,-1.94+(i//3)*.06,.36),(.09,.06,.075),'wall_light',1)
    for i in range(7): g.ico('Workshop stone chip',(.28+i*.15,-1.96,.025),(.055,.045,.04),'wall_light',1)
    dress()


def scales(pos):
    x,y,z=pos
    g.lathe('Scale base',[(0,.12),(.04,.12)],'gold',12,pos)
    g.beam('Scale upright',(x,y,z),(x,y,z+.41),.032,.035,'gold')
    g.beam('Scale balance beam',(x-.26,y,z+.38),(x+.26,y,z+.41),.031,.032,'gold')
    for s in [-1,1]:
        cx=x+s*.22
        for dy in [-.08,.08]: g.tube('Scale pan chain',[(cx,y,z+.39),(cx,y+dy,z+.18)],.008,'gold',6)
        g.lathe('Scale bowl',[(0,.06),(.04,.105)],'gold',10,(cx,y,z+.15),caps=False)


def trade_market():
    cottage_shell(stone=False); cottage.window(0,-.99,2.24,.40,.66)
    canopy(0,-1.0,1.96,2.18,.92,True)
    table((0,-1.60,0),1.98,.58,.78)
    for x,y,s in [(-.66,-1.59,.70),(-.16,-1.65,.53),(.22,-1.51,.65)]: kit.place('parcel',(x,y,.84),s)
    group('Hero market balance scales',lambda:scales((0,0,0)),(.53,-1.62,.85),1.65)
    for i in range(10): g.lathe('Market gold coin',[(0,.041),(.018,.041)],'gold',10,(.30+(i%3)*.08,-1.72+(i//3)*.045,.84+(i%2)*.018))
    group('Side market canopy',lambda:canopy(0,-1.0,1.72,1.27,.62),(-.10,.11,0),rotation=(0,0,-math.pi/2))
    kit.place('crate',(-1.50,-.54,0),1.10); kit.place('crate',(-1.52,.02,0),1.18)
    kit.place('parcel',(-1.52,.02,.56),.82)
    banner((-1.73,-.83,1.60),'rook',.34,.67,'red')
    lantern_arm((-1.75,-1.04,1.83))
    g.cube('Market chest',(-1.51,-1.26,.22),(.59,.38,.42),'wood',.035)
    g.tube('Chest arched lid',[(-1.79,-1.26,.45),(-1.23,-1.26,.45)],.205,'wood_light',10)
    for x in [-1.72,-1.3]: g.cube('Chest iron band',(x,-1.455,.24),(.035,.025,.38),'iron',.005)
    g.cube('Chest lock',(-1.51,-1.47,.34),(.085,.027,.10),'gold',.013)
    g.cube('Trade sign post',(1.57,-.14,1.41),(.14,.14,2.82),'wood_light')
    sign((1.73,-.35,2.75),'scales')
    kit.place('crate',(1.40,-.93,0),1.05)
    for i,mat in enumerate(['blue','red','cream']): g.tube('Rolled market fabric',[(1.30+i*.10,-.94,.47),(1.30+i*.10,-.94,.92)],.08,mat,10)
    kit.place('barrel',(.95,-1.95,0),.64)
    kit.place('barrel',(-1.49,.86,0),.83)
    kit.place('parcel',(1.15,.82,0),1.17); kit.place('parcel',(1.17,.86,.37),.72)
    dress()


def magic_academy():
    cottage_shell(); dormer((.60,-.22,2.57))
    cottage.door(-.18,-.98,.20,.62,1.40); stairs(-.18,-1.46,.23,3,.81)
    stone_arch(-.18,-1.015,.20,.62,1.40)
    group('Academy side window',lambda:cottage.window(0,-1.15,.94,.42,.71),rotation=(0,0,-math.pi/2))
    glyph('eye',-.18,-1.08,1.25,.38,'window')
    banner((0,-1.22,2.95),'eye',.80,.99)
    # Round turret uses alternating joints around all sides, with a tiled conical roof.
    cx,cy=.79,.68
    g.lathe('Academy round turret core',[(0,.55),(3.48,.55)],'stone_light',12,(cx,cy,0))
    for row in range(11):
        for i in range(12):
            angle=(i+(row%2)*.5)*math.tau/12
            kit.place('stone_block',(cx+.515*math.cos(angle),cy+.515*math.sin(angle),row*.315),(.71,.42,1.05),(0,0,angle+math.pi/2))
    group('Turret glowing window',lambda:cottage.window(0,-.568,2.56,.26,.57),(cx,cy,0))
    g.lathe('Turret cone backing',[(3.42,.79),(4.75,.02)],'roof_blue_dark',12,(cx,cy,0))
    for row in range(4):
        z=3.43+row*.32; radius=.84*(1-row/4)
        roof=g.lathe('Broad stepped turret roof',[(z-.06,radius-.04),(z,radius),(z+.35,max(.025,radius-.23))],
                     'roof_blue',12,(cx,cy,0))
        g.facet_colors(roof,['roof_blue','roof_blue','roof_blue_light'])
    g.lathe('Crystal gold mount',[(4.68,.16),(4.75,.23),(4.88,.23)],'gold',6,(cx,cy,0))
    crystal=g.lathe('Academy purple crystal',[(4.82,0),(5.13,.29),(5.68,0)],'magic',6,(cx,cy,0))
    g.facet_colors(crystal,['magic','purple_light'])
    for a in range(4):
        angle=a*math.pi/2
        g.tube('Crystal crown prong',[(cx+.17*math.cos(angle),cy+.17*math.sin(angle),4.72),(cx+.27*math.cos(angle),cy+.27*math.sin(angle),5.00)],.05,'gold',6)
    # Open book on lectern, separate page sheets with engraved lines.
    g.cube('Reading lectern post',(-1.30,-1.24,.38),(.13,.13,.76),'wood_light')
    g.cube('Lectern reading board',(-1.30,-1.24,.81),(.64,.42,.08),'wood_edge',.025,(.25,0,0))
    for s in [-1,1]:
        g.cube('Open magic book pages',(-1.30+s*.145,-1.24,.875),(.29,.36,.035),'cream',.008,(.25,s*.14,0))
        for i in range(4): g.beam('Book ink line',(-1.30+s*.145-.09,-1.36+i*.06,.886+i*.015),(-1.30+s*.145+.09,-1.36+i*.06,.886+i*.015),.008,.008,'wood',0)
    for i in range(3): kit.place('book',(-1.22,-1.13,i*.10),1.0,(0,0,(i-1)*.12))
    g.lathe('Academy candle',[(0,.065),(.24,.065)],'cream',10,(-1.55,-1.13,.84))
    g.lathe('Candle flame',[(0,.045),(.10,.032),(.20,0)],'window',8,(-1.55,-1.13,1.08))
    g.lathe('Orb stone pedestal',[(0,.23),(.09,.24),(.15,.13),(.52,.13),(.60,.25)],'wall_light',8,(1.32,-1.16,0))
    g.ico('Academy glowing orb',(1.32,-1.16,1.03),(.38,)*3,'magic',2,.01)
    for i in range(4):
        a=i*math.pi/2
        g.tube('Orb golden cradle',[(1.32,-1.16,.58),(1.32+.38*math.cos(a),-1.16+.38*math.sin(a),.83),(1.32+.33*math.cos(a),-1.16+.33*math.sin(a),1.02)],.045,'gold',6)
    lantern_arm((-.83,-.98,1.8)); banner((1.68,-.18,2.86),'eye',.85,1.08,'purple')
    g.beam('Academy sign arm',(1.06,.03,2.65),(1.89,.03,2.65),.12,.12,'wood_light')
    dress(); front_path()


BUILDERS={name:globals()[name] for name in ['arrow_tower','bombarding_tower','barracks','stone_cutter','tavern','trade_market','magic_academy']}
