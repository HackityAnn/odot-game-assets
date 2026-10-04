"""Four original buildings, using the supplied image as the art reference."""
import math
import bpy
from mathutils import Vector
import geometry as g


def relief(name, outline, y, depth, mat, bevel=.015):
    """A closed silhouette with an actual edge, for readable signs and emblems."""
    n=len(outline)
    verts=[(x,yy,z) for yy in [y,y+depth] for x,z in outline]
    faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]
    faces += [(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
    return g.mesh(name,verts,faces,mat,bevel)


def portal(x,y,bottom,width,height):
    """Carve a shallow arched recess in the structural wall, before its trim."""
    radius=width/2; spring=bottom+height-radius
    outline=[(x-radius,bottom-.04),(x+radius,bottom-.04),(x+radius,spring)]
    outline += [(x+radius*math.cos(i*math.pi/12),spring+radius*math.sin(i*math.pi/12)) for i in range(1,13)]
    cutter=relief('Temporary arched pocket',outline,y-.22,.60,'shadow',0)
    bpy.context.view_layer.update()
    for obj in list(g.CURRENT.objects):
        if obj.type!='MESH' or not obj.get('wall_surface'): continue
        bounds=[obj.matrix_world @ Vector(v) for v in obj.bound_box]
        if (max(v.x for v in bounds)<x-radius or min(v.x for v in bounds)>x+radius
                or max(v.y for v in bounds)<y-.22 or min(v.y for v in bounds)>y+.38
                or max(v.z for v in bounds)<bottom or min(v.z for v in bounds)>bottom+height): continue
        # Shared masonry stays reusable; this instance owns its carved mesh.
        if obj.data.users>1: obj.data=obj.data.copy()
        mod=obj.modifiers.new('Recessed architectural opening','BOOLEAN')
        mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)


def bread(pos, size=(.42,.20,.20)):
    x,y,z=pos; sx,sy,sz=size
    g.ico('Hero golden bread loaf',pos,size,'gold',3,.015)
    for offset in [-.48,0,.48]:
        xx=x+offset*sx
        g.tube('Broad bread scoring',[(xx-.045,y-sy*.62,z+sz*.68),(xx,y,z+sz*.96),(xx+.045,y+sy*.62,z+sz*.68)],.024,'cream',6)


def timber_depth():
    """Large projecting joints and side bracing, rather than extra tiny detail."""
    for x in [-1.01,1.01]:
        for y in [-.89,.89]:
            g.cube('Projecting timber footing',(x,y,.21),(.34,.34,.42),'wood_edge',.045)
            g.cube('Heavy timber capital',(x,y,1.96),(.36,.36,.32),'wood_light',.035)
            g.beam('Eave knee brace',(x,y,1.55),(x*1.38,y,2.05),.19,.20,'wood_edge',.025)
        g.beam('Side wall lower tie',(x, -.82,.37),(x,.82,.37),.18,.20,'wood_dark')
        g.beam('Side wall diagonal',(x*1.065,-.77,.46),(x*1.065,.73,1.81),.15,.15,'wood_edge')
    for y in [-1.20,1.20]:
        for x,z in [(0,3.33),(-1.42,2.08),(1.42,2.08)]:
            g.cube('Chunky roof joinery',(x,y,z),(.30,.30,.35),'wood_edge',.035)


def arch(name, x, y, bottom, width, height, mat='window'):
    radius=width/2; spring=bottom+height-radius
    points=[(x-radius,y,bottom),(x+radius,y,bottom),(x+radius,y,spring)]
    points += [(x+radius*math.cos(i*math.pi/10),y,spring+radius*math.sin(i*math.pi/10)) for i in range(1,11)]
    return g.mesh(name,points,[tuple(range(len(points)))],mat)


def window(x,y,z,width=.48,height=.70):
    arch('Window dark recess',x,y,z,width+.12,height+.08,'wood_dark')
    arch('Warm arched window',x,y-.015,z+.035,width,height-.02)
    r=(width+.055)/2; spring=z+height-r+.055
    points=[(x-r,y-.025,z),(x-r,y-.025,spring)]
    points += [(x+r*math.cos(math.pi-i*math.pi/12),y-.025,spring+r*math.sin(math.pi-i*math.pi/12)) for i in range(1,13)]
    points += [(x+r,y-.025,z)]
    g.tube('Arched window frame',points,.035,'wood_light',6)
    g.beam('Window mullion',(x,y-.045,z),(x,y-.045,z+height),.04,.045,'wood_light',.008)
    g.beam('Window transom',(x-width*.48,y-.045,z+height*.43),(x+width*.48,y-.045,z+height*.43),.045,.04,'wood_light',.008)
    g.cube('Window sill',(x,y-.07,z-.015),(width+.20,.18,.075),'wood_edge',.015)


def door(x,y,z,width=.60,height=1.15):
    portal(x,y,z,width+.16,height+.1)
    arch('Doorway recess',x,y+.30,z,width+.16,height+.1,'shadow')
    for i in range(5):
        xx=x+(i-2)*width/5
        r=width/2
        top=z+height-r+math.sqrt(max(0,r*r-(xx-x)**2))
        g.cube('Door plank',(xx,y+.15,(z+top)/2),(width/5-.009,.08,top-z),'wood_light',.015)
    for dz in [.22,.73]: g.cube('Door iron strap',(x,y+.095,z+dz),(width*.9,.045,.085),'wood_dark',.01)
    g.ico('Door brass handle',(x+width*.25,y+.05,z+.51),(.05,.035,.05),'gold',2)
    r=width/2+.06; spring=z+height-width/2
    points=[(x-r,y-.045,z),(x-r,y-.045,spring)]
    points += [(x+r*math.cos(math.pi-i*math.pi/10),y-.045,spring+r*math.sin(math.pi-i*math.pi/10)) for i in range(1,11)]
    points += [(x+r,y-.045,z)]
    g.tube('Heavy doorway frame',points,.055,'wood_dark',6)


def cottage_body(stone=False):
    previous=set(g.CURRENT.objects)
    g.cube('Cottage walls',(0,0,1.15),(1.98,1.72,2.15),'wall' if stone else 'wood_dark',.045)
    if not stone:
        for x in [-.87,-.60,-.33,-.06,.21,.48,.75]:
            for y in [-.882,.882]:
                g.cube('Wall timber board',(x,y,1.1),(.25,.06,2.03),g.RNG.choice(['wood','wood_light']),.015)
        for y in [-.74,-.47,-.20,.07,.34,.61]:
            for x in [-1.012,1.012]:
                g.cube('Side timber board',(x,y,1.10),(.06,.25,2.03),g.RNG.choice(['wood','wood_light']),.012)
    else:
        for row in range(5):
            for i in range(4):
                x=-.75+i*.50
                g.cube('Front limestone block',(x,-.88,.24+row*.40),(.48,.18,.38),g.RNG.choice(['wall','wall_light']),.045)
                for side in [-1,1]:
                    g.cube('Side limestone block',(side*1.0,-.64+i*.425,.24+row*.40),(.18,.405,.38),g.RNG.choice(['wall','wall_light']),.04)
    for y in [-.89,.89]:
        g.mesh('Timber gable',[(-1,y,2.20),(1,y,2.20),(0,y,3.14)],[(0,1,2)],'wood')
        for x in [-.8,-.4,0,.4,.8]:
            top=3.13-abs(x)*.92
            g.cube('Gable vertical board',(x,y-.015,(2.2+top)/2),(.28,.12,top-2.2),'wood_light',.018)
        g.beam('Gable tie beam',(-1.1,y-.06,2.18),(1.1,y-.06,2.18),.15,.15,'wood_dark')
        g.beam('Gable brace',(-.92,y-.06,2.2),(0,y-.06,3.1),.15,.13,'wood_dark')
        g.beam('Gable brace',(.92,y-.06,2.2),(0,y-.06,3.1),.15,.13,'wood_dark')
        g.beam('Gable king post',(0,y-.07,2.2),(0,y-.07,3.17),.14,.14,'wood_dark')
    for x in [-.99,.99]:
        for y in [-.88,.88]: g.cube('Corner upright',(x,y,1.15),(.27,.27,2.30),'wood_light',.035)
    for z in [.19,1.92]:
        for y in [-.925,.925]: g.cube('Wall cross beam',(0,y,z),(2.16,.16,.17),'wood_dark')
    for obj in set(g.CURRENT.objects)-previous:
        if obj.name.startswith(('Cottage walls','Front limestone','Side limestone','Wall timber board','Side timber board')):
            obj['wall_surface']=True
    timber_depth()


def roof(color='blue'):
    slope=.82; angle=math.atan(slope); peak=3.21
    for sign in [-1,1]:
        g.cube('Roof underlay',(sign*.64,0,peak-.64*slope),(1.75,2.25,.13),'wood_dark',.02,(0,sign*angle,0))
        for row in range(4):
            x=sign*(.16+row*.35)
            for col in range(5):
                y=-.92+col*.46+(row%2)*.035
                z=peak-abs(x)*slope+.06
                g.cube('Overlapping roof tile',(x,y,z),(.55,.48,.12),
                       g.RNG.choice([f'roof_{color}',f'roof_{color}',f'roof_{color}_light']),.04,
                       (0,sign*angle,g.RNG.uniform(-.018,.018)))
        for y in [-1.18,1.18]:
            g.beam('Carved roof verge',(0,y,peak+.05),(sign*1.48,y,peak-1.48*slope),.25,.24,'wood_light')
        g.beam('Roof eave',(sign*1.43,-1.16,2.02),(sign*1.43,1.16,2.02),.13,.17,'wood_dark')
    g.beam('Ridge timber',(0,-1.32,3.32),(0,1.35,3.32),.19,.21,'wood_light')
    for y in [-1.14,.05,1.10]:
        g.cube('Ridge peg',(0,y,3.39),(.25,.20,.26),'wood_edge',.022)


def chimney(x=.65,y=.50):
    for row in range(6):
        g.cube('Chimney stone course',(x,y,2.62+row*.23),(.42,.43,.217),
               g.RNG.choice(['stone_light','wall','stone']),.023)
        # Mortar divisions wrap onto both visible faces.
        g.cube('Chimney mortar joint',(x+(-.10 if row%2 else .09),y-.219,2.62+row*.23),(.018,.008,.217),'stone_dark',0)
        g.cube('Chimney side mortar',(x+.215,y+(-.08 if row%2 else .08),2.62+row*.23),(.008,.018,.217),'stone_dark',0)
    for dx,dy,sx,sy in [(-.22,0,.10,.54),(.22,0,.10,.54),(0,-.22,.36,.10),(0,.22,.36,.10)]:
        g.cube('Open chimney rim',(x+dx,y+dy,3.98),(sx,sy,.14),'wall_light',.02)
    g.cube('Chimney dark opening',(x,y,3.92),(.35,.35,.025),'shadow',0)


def wood_grain(a,b):
    g.beam('Carved wood grain',a,b,.012,.008,'wood_dark',0)


def woodcutter_hut():
    cottage_body(); roof('blue'); chimney()
    door(.28,-.935,.04,.64,1.45)
    window(-.45,-.965,.67,.43,.70)
    # Lean-to shelters stacked firewood on the left of the cottage.
    for x in [-1.95,-1.00]:
        for y in [-.78,.65]: g.cube('Lean-to upright',(x,y,.75),(.15,.16,1.5),'wood_light')
    for i in range(5):
        y=-.79+i*.32
        g.cube('Lean-to roof plank',(-1.5,y,1.62),(1.19,.33,.13),'wood_light',.025,(0,-.12,0))
    g.beam('Lean-to header',(-2.1,-.99,1.50),(-.9,-.99,1.65),.20,.16,'wood_edge')
    for row in range(3):
        for col in range(3-row%2):
            g.log((-1.78+col*.31+row%2*.12,-.62,.18+row*.29),.95,.145)
    for row in range(3):
        for col in range(2): g.log((1.12+col*.28,-.10,.16+row*.27),.74,.135)
    for x,y,r,h in [(-1.35,-1.44,.25,.46),(.94,-1.58,.23,.36),(1.54,-1.18,.30,.43)]:
        g.log((x,y,0),h,r,'Z')
    g.beam('Hero axe handle',(-1.34,-1.44,.42),(-.95,-1.39,1.49),.115,.10,'wood_light',.02)
    relief('Hero axe broad blade',[(-1.22,1.28),(-.61,1.16),(-.51,1.58),(-1.15,1.56)],-1.48,.15,'silver',.035)
    g.cube('Woodcutter hanging log sign',(-1.43,-1.50,2.00),(.97,.18,.61),'wood_light',.07)
    g.beam('Log sign bracket',(-1.94,-1.50,2.49),(-.93,-1.50,2.49),.17,.17,'wood_edge')
    g.beam('Log sign wall arm',(-.96,-.89,2.49),(-1.43,-1.50,2.49),.16,.16,'wood_edge')
    for x in [-1.76,-1.10]: g.tube('Log sign hanger',[(x,-1.50,2.43),(x,-1.50,2.29)],.025,'silver_dark',6)
    g.tube('Raised log sign emblem',[(-1.60,-1.64,1.98),(-1.16,-1.64,2.15)],.17,'bark',10)
    g.tube('Log sign endgrain',[(-1.64,-1.66,1.98),(-1.61,-1.66,1.99)],.145,'wood_edge',10)
    for i in range(4): g.stepping_stone((.30+(i%2)*.10,-1.18-i*.27),.21)
    g.shrub((.68,-.25,2.77),.25)
    for a,b in [((1.86,.23,0),(1.86,1.48,0)),((.8,1.7,0),(1.75,1.7,0))]: g.fence(a,b,3,.60)


def bakery():
    cottage_body(True); roof('red'); chimney(.66,.51)
    # The door opening sits behind the market canopy; warm loaves read at game distance.
    portal(.46,-.972,.20,.88,1.23)
    arch('Bakery oven opening',.46,-.68,.20,.88,1.23,'shadow')
    window(-.48,-.985,.63,.46,.72)
    g.cube('Bakery threshold',(.47,-1.09,.13),(.95,.39,.25),'stone_light',.04)
    g.cube('Bakery step',(.47,-1.39,.05),(.86,.30,.10),'stone',.025)
    # Gently curved striped awning, modeled as solid cloth strips.
    for i in range(6):
        x=-.02+i*.185
        profile=[(-.97,1.93),(-1.08,1.88),(-1.24,1.67),(-1.42,1.54),(-1.55,1.52)]
        verts=[(x+sign*.094,y,z) for y,z in profile for sign in [-1,1]]
        cloth=g.mesh('Continuous striped fabric canopy',verts,
                     [(j*2,j*2+1,j*2+3,j*2+2) for j in range(len(profile)-1)],
                     'cream' if i%2 else 'roof_red_light')
        mod=cloth.modifiers.new('Canvas thickness','SOLIDIFY'); mod.thickness=.03
        g.cube('Scalloped canopy edge',(x,-1.53,1.43),(.19,.045,.16),'cream' if i%2 else 'roof_red_light',.055)
    for x in [-.14,1.08]: g.beam('Canopy support',(x,-.91,1.89),(x,-1.52,1.43),.05,.05,'wood_light',.008)
    g.cube('Baker market counter',(.58,-1.55,.65),(1.40,.54,.14),'wood_edge',.035)
    for x in [-.01,1.17]:
        for y in [-1.73,-1.38]: g.cube('Market counter leg',(x,y,.31),(.115,.115,.63),'wood_light')
    g.cube('Counter lower shelf',(.58,-1.55,.20),(1.29,.45,.07),'wood',.015)
    for i in range(3):
        bread((.12+i*.46,-1.55,.90),(.25,.18,.20))
    for i in range(3): g.ico('Oven bread loaf',(.25+i*.19,-1.02,.33),(.13,.11,.09),'gold',2)
    g.barrel((-1.25,-.72,0),1.15); g.crate((-1.03,-1.42,0),.43)
    g.cube('Bakery sign post',(-1.13,.02,1.88),(.14,.16,3.50),'wood_light')
    g.beam('Bakery hanging sign beam',(-1.65,-.04,3.32),(-.12,-.04,3.32),.18,.16,'wood_edge')
    for x in [-1.74,-1.02]: g.tube('Sign chain',[(x,-.36,3.25),(x,-.36,3.00)],.026,'silver_dark',6)
    g.beam('Forward bread sign bracket',(-1.31,-.04,3.30),(-1.31,-.42,3.30),.17,.17,'wood_edge')
    g.cube('Bakery wooden sign',(-1.38,-.36,2.62),(1.22,.22,.81),'wood_light',.10)
    bread((-1.38,-.51,2.62),(.44,.10,.23))
    g.lantern((1.46,-.70,.73),1.1)
    for i in range(4): g.stepping_stone((-.09-i*.13,-1.15-i*.30),.23)
    g.fence((-1.93,-.72,0),(-1.93,1.17,0),4)


def gold_mine():
    # Dark cavity is deliberately open behind its beam portal, rather than a painted doorway.
    for x,y,z,sx,sy,sz in [(-1.21,.24,.80,.73,.84,.98),(1.16,.30,.75,.61,.78,.91),
                           (-.79,.70,1.62,.68,.74,1.16),(.46,.85,2.07,.80,.72,1.30),
                           (1.04,1.04,1.04,.59,.70,.85),(-1.60,.06,.23,.50,.55,.46),
                           (1.57,.50,.29,.45,.62,.53),(-.33,1.37,.97,.68,.66,.89)]:
        obj=g.ico('Mine outcrop',(x,y,z),(sx,sy,sz),'stone',2,.10)
        g.facet_colors(obj,['stone','stone_light','stone_dark'])
    g.mesh('Mine tunnel darkness',[(-.73,.73,.03),(.73,.73,.03),(.73,.73,1.69),(-.73,.73,1.69)],[(0,1,2,3)],'shadow')
    for x in [-.72,.72]:
        g.cube('Mine portal upright',(x,-.44,.82),(.24,.27,1.64),'wood_light',.035)
        g.cube('Portal foot',(x,-.44,.12),(.34,.37,.24),'wood_dark',.025)
    g.cube('Heavy mine lintel',(0,-.47,1.79),(1.94,.35,.30),'wood_edge',.035)
    for x in [-.76,.76]:
        g.beam('Portal diagonal brace',(x,-.43,1.15),(x*.39,-.43,1.65),.17,.18,'wood')
    for x in [-.77,.77]:
        g.ico('Portal iron nail',(x,-.65,1.78),(.045,.013,.045),'silver_dark',2,0)
    # Tracks continue through the portal; cart sits on the rails.
    for y in [-1.98,-1.60,-1.22,-.84,-.46,-.08,.30]:
        g.cube('Railway timber sleeper',(0,y,.045),(1.14,.16,.09),'wood_dark',.015)
    for x in [-.37,.37]:
        g.tube('Mine iron rail',[(x,.61,.10),(x,-1.15,.10),(x+.09,-1.63,.10),(x+.19,-2.05,.10)],.045,'silver_dark',6)
    cx,cy=.07,-1.08
    g.cube('Minecart chassis',(cx,cy,.34),(1.00,.88,.14),'wood_dark')
    for x in [-.47,.47]:
        for y in [-.30,.30]:
            g.tube('Minecart iron wheel',[(cx+x-.05,cy+y,.24),(cx+x+.05,cy+y,.24)],.19,'silver_dark',12)
            g.tube('Wheel hub',[(cx+x-.06,cy+y,.24),(cx+x+.065,cy+y,.24)],.065,'wood_edge',10)
    for side in [-1,1]:
        g.cube('Cart side',(cx+side*.46,cy,.63),(.09,.89,.49),'wood_light',.025)
        g.cube('Cart end',(cx,cy+side*.39,.63),(.87,.10,.49),'wood_light',.025)
        g.cube('Cart iron side rim',(cx+side*.48,cy,.91),(.095,1.0,.095),'silver_dark',.018)
        g.cube('Cart iron end rim',(cx,cy+side*.44,.91),(1.03,.10,.095),'silver_dark',.018)
    for i in range(7):
        x=cx+g.RNG.uniform(-.33,.33); y=cy+g.RNG.uniform(-.29,.29)
        g.ico('Cart gold ore',(x,y,1.00+g.RNG.uniform(0,.16)),(.24,.22,.23),g.RNG.choice(['gold','gold_light']),1)
    g.cube('Mine projecting lintel cap',(0,-.50,1.98),(2.12,.48,.16),'wood_light',.035)
    relief('Gold mine raised ore emblem',[(-.40,2.06),(-.23,2.32),(.10,2.37),(.36,2.16),(.25,2.00),(-.18,1.97)],-.77,.10,'gold',.025)
    for x in [-.79,.79]:
        g.beam('Mine portal deep side beam',(x,-.44,1.63),(x,.43,1.63),.23,.23,'wood_light')
        g.cube('Mine portal front capital',(x,-.48,1.75),(.42,.43,.37),'wood_edge',.04)
    for x,y,s in [(-.98,-1.22,.18),(1.13,-1.45,.21),(1.57,-.98,.15)]: g.ico('Scattered gold',(x,y,.11),(s,s*.83,s*.9),'gold',1)
    for p in [(-.94,-.41,.23),(.91,-.32,.29)]: g.lantern(p,.95)
    g.cube('Mine lantern post',(1.39,.95,1.23),(.15,.16,2.46),'wood_light')
    g.beam('Mine lantern arm',(1.39,.95,2.32),(1.94,.95,2.32),.15,.15,'wood_edge')
    g.tube('Lantern hanging hook',[(1.87,.95,2.28),(1.87,.95,1.92)],.017,'silver_dark',6)
    g.lantern((1.87,.95,1.65),1.1)
    for p in [(-1.64,-.62,0),(.82,1.12,0)]: g.crate(p,.44)
    for p in [(-.82,.25,2.33),(.36,.24,2.97),(-1.22,-.20,.77),(1.47,.67,.68)]: g.shrub(p,.25)


def tree_house():
    # Branching low-sided trunk with a flared root skirt.
    trunk=g.tube('Ancient hollow tree',[(0,0,.03),(-.13,.07,.62),(-.05,.02,1.45),(.16,.09,2.17),(.06,.12,3.12)],
                 [.66,.46,.42,.40,.25],'bark',9)
    g.facet_colors(trunk,['bark','bark_light','wood'])
    for i in range(8):
        a=i*math.tau/8+.15
        p=(math.cos(a),math.sin(a),.05)
        g.tube('Spreading tree root',[(.17*math.cos(a),.17*math.sin(a),.85),
                                     (.56*math.cos(a),.56*math.sin(a),.22),p], [.23,.21,.04],'bark',7)
    branches=[((.03,.10,2.04),(-.98,.1,3.20),(-1.28,.10,3.43)),
              ((.12,.15,2.48),(1.03,.16,3.38),(1.37,.07,3.69)),
              ((.09,.05,2.43),(.27,.64,3.70),(.48,.87,4.0)),
              ((.02,0,2.4),(-.63,-.72,3.35),(-.79,-.87,3.66))]
    for a,b,c in branches: g.tube('Twisting canopy branch',[a,b,c],[.23,.15,.045],'bark_light',7)
    # Small timber room nested into the front of the tree.
    g.cube('Treehouse room',(0,-.34,2.31),(1.14,.88,1.02),'wood_dark',.04)
    for i in range(6): g.cube('Treehouse wall board',(-.48+i*.195,-.80,2.30),(.19,.07,1.0),'wood_light',.015)
    g.mesh('Treehouse front gable',[(-.61,-.83,2.83),(.61,-.83,2.83),(0,-.83,3.37)],[(0,1,2)],'wood')
    for sign in [-1,1]:
        for i in range(3):
            g.cube('Treehouse shingle',(sign*(.13+i*.22),-.31,3.37-(.13+i*.22)*.87),(.35,1.15,.08),'bark_light',.03,(0,sign*.715,0))
        g.beam('Treehouse gable verge',(0,-.94,3.45),(sign*.78,-.94,2.79),.16,.14,'wood_dark')
    window(0,-.875,2.18,.52,.65)
    # Front balcony with rails, braces, and a staircase reaching the actual ground.
    for i in range(9): g.cube('Balcony floor board',(-.86+i*.215,-.79,1.85),(.21,.93,.12),'wood_edge',.018)
    for x in [-.82,.0,.82]:
        g.beam('Balcony support',(x*.30,-.08,1.10),(x,-1.02,1.79),.16,.16,'wood')
    for x in [-.91,-.45,0,.45,.91]: g.cube('Balcony railing post',(x,-1.19,2.10),(.15,.15,.53),'wood_light',.025)
    for z in [1.99,2.26]: g.beam('Balcony front rail',(-1,-1.19,z),(1,-1.19,z),.11,.10,'wood_edge',.012)
    for x in [-.97,.97]:
        for z in [1.99,2.26]: g.beam('Balcony side rail',(x,-1.19,z),(x,-.33,z),.11,.10,'wood_edge',.012)
    for i in range(10):
        y=-2.00+i*.14; z=.085+i*.185
        g.cube('Tree stair tread',(-.34,y,z),(.64,.24,.10),'wood_edge',.017)
        g.cube('Tree stair riser',(-.34,y+.06,z-.07),(.59,.045,.12),'wood',.01)
    for x in [-.65,-.03]: g.beam('Stair stringer',(x,-2.10,.0),(x,-.68,1.79),.12,.14,'wood_dark',.015)
    # Upper roots are bridged by a second small landing.
    for i in range(4): g.cube('Tree landing plank',(-.33,-.86-i*.12,1.46),(.72,.12,.085),'wood_light',.012)
    # Cloth banner, visible below the balcony.
    relief('Blue treehouse banner',[(.39,1.92),(1.08,1.92),(1.08,.84),(.735,1.02),(.39,.84)],-1.34,.05,'blue')
    for a,b in [((.69,-1.313,1.28),(.69,-1.313,1.73)),((.69,-1.313,1.54),(.58,-1.313,1.65)),
                ((.69,-1.313,1.48),(.81,-1.313,1.61))]:
        a=(a[0]+.04,-1.39,a[2]); b=(b[0]+.04,-1.39,b[2])
        g.beam('Banner white tree emblem',a,b,.052,.04,'cream',.008)
    for sign in [-1,1]:
        g.beam('Treehouse deep balcony bracket',(sign*.31,-.24,1.03),(sign*.86,-1.11,1.80),.24,.22,'bark_light')
        g.cube('Treehouse room corner post',(sign*.60,-.82,2.34),(.18,.18,1.15),'wood_edge')
    canopy=[(-1.04,.08,3.53,.71),(-.59,.63,3.93,.77),(.02,.46,4.46,.89),
            (.76,.48,4.11,.79),(1.27,.07,3.68,.70),(.68,-.51,3.45,.76),
            (-.38,-.61,3.63,.75),(-1.24,-.47,3.31,.58),(.15,1.0,3.75,.66)]
    for x,y,z,s in canopy:
        crown=g.ico('Faceted broadleaf crown',(x,y,z),(s,s*.78,s*.72),'leaf',2,.09)
        g.facet_colors(crown,['leaf','leaf_light','leaf_dark'])
    g.beam('Tree lantern branch',(-.65,-.21,2.61),(-1.48,-.39,2.44),.10,.11,'bark')
    g.tube('Tree lantern hanger',[(-1.43,-.39,2.46),(-1.43,-.39,2.04)],.015,'wood_dark',6)
    g.lantern((-1.43,-.39,1.80),1.1)
    g.fence((-1.55,-.96,0),(-1.78,.93,0),4,.70)
    g.fence((1.42,-.47,0),(1.64,1.02,0),3,.70)
    g.shrub((.27,-.83,2.06),.20); g.shrub((.93,-.16,.12),.32)
    g.mushroom((-1.15,-1.58,0),.32,'red'); g.mushroom((1.18,-1.26,0),.35)


BUILDERS={'woodcutter_hut':woodcutter_hut,'bakery':bakery,'gold_mine':gold_mine,'tree_house':tree_house}
