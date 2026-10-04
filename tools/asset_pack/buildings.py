"""Four original buildings, using the supplied image as the art reference."""
import math
from mathutils import Vector
import geometry as g


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
    arch('Doorway recess',x,y,z,width+.16,height+.1,'shadow')
    for i in range(5):
        xx=x+(i-2)*width/5
        r=width/2
        top=z+height-r+math.sqrt(max(0,r*r-(xx-x)**2))
        g.cube('Door plank',(xx,y-.025,(z+top)/2),(width/5-.009,.045,top-z),'wood_light',.008)
    for dz in [.22,.73]: g.cube('Door iron strap',(x,y-.059,z+dz),(width*.9,.025,.065),'wood_dark',.006)
    g.ico('Door brass handle',(x+width*.25,y-.09,z+.51),(.038,.022,.038),'gold',2)
    r=width/2+.06; spring=z+height-width/2
    points=[(x-r,y-.045,z),(x-r,y-.045,spring)]
    points += [(x+r*math.cos(math.pi-i*math.pi/10),y-.045,spring+r*math.sin(math.pi-i*math.pi/10)) for i in range(1,11)]
    points += [(x+r,y-.045,z)]
    g.tube('Heavy doorway frame',points,.055,'wood_dark',6)


def cottage_body(stone=False):
    g.cube('Cottage walls',(0,0,1.15),(1.98,1.72,2.15),'wall' if stone else 'wood_dark',.045)
    if not stone:
        for x in [-.87,-.60,-.33,-.06,.21,.48,.75]:
            for y in [-.882,.882]:
                g.cube('Wall timber board',(x,y,1.1),(.25,.06,2.03),g.RNG.choice(['wood','wood_light']),.015)
        for y in [-.74,-.47,-.20,.07,.34,.61]:
            for x in [-1.012,1.012]:
                g.cube('Side timber board',(x,y,1.10),(.06,.25,2.03),g.RNG.choice(['wood','wood_light']),.012)
    else:
        for row in range(6):
            for i in range(6):
                x=-.86+i*.34+(row%2)*.08
                g.cube('Front limestone block',(x,-.88,.20+row*.33),(.325,.07,.305),g.RNG.choice(['wall','wall_light','stone_light']),.025)
                g.cube('Side limestone block',(1.0,-.72+i*.285,.20+row*.33),(.08,.27,.305),g.RNG.choice(['wall','wall_light']),.02)
    for y in [-.89,.89]:
        g.mesh('Timber gable',[(-1,y,2.20),(1,y,2.20),(0,y,3.14)],[(0,1,2)],'wood')
        for x in [-.8,-.4,0,.4,.8]:
            top=3.13-abs(x)*.92
            g.cube('Gable vertical board',(x,y-.015,(2.2+top)/2),(.28,.05,top-2.2),'wood_light',.012)
        g.beam('Gable tie beam',(-1.1,y-.06,2.18),(1.1,y-.06,2.18),.15,.15,'wood_dark')
        g.beam('Gable brace',(-.92,y-.06,2.2),(0,y-.06,3.1),.15,.13,'wood_dark')
        g.beam('Gable brace',(.92,y-.06,2.2),(0,y-.06,3.1),.15,.13,'wood_dark')
        g.beam('Gable king post',(0,y-.07,2.2),(0,y-.07,3.17),.14,.14,'wood_dark')
    for x in [-.99,.99]:
        for y in [-.88,.88]: g.cube('Corner upright',(x,y,1.15),(.17,.17,2.30),'wood_dark')
    for z in [.19,1.92]:
        for y in [-.925,.925]: g.cube('Wall cross beam',(0,y,z),(2.16,.16,.17),'wood_dark')


def roof(color='blue'):
    slope=.82; angle=math.atan(slope); peak=3.21
    for sign in [-1,1]:
        g.cube('Roof underlay',(sign*.64,0,peak-.64*slope),(1.75,2.25,.13),'wood_dark',.02,(0,sign*angle,0))
        for row in range(5):
            x=sign*(.12+row*.268)
            for col in range(7):
                y=-.99+col*.325+(row%2)*.035
                z=peak-abs(x)*slope+.06
                g.cube('Overlapping roof tile',(x,y,z),(.405,.337,.065),
                       g.RNG.choice([f'roof_{color}',f'roof_{color}_light',f'roof_{color}_dark']),.028,
                       (0,sign*angle,g.RNG.uniform(-.018,.018)))
        for y in [-1.18,1.18]:
            g.beam('Carved roof verge',(0,y,peak+.05),(sign*1.48,y,peak-1.48*slope),.18,.16,'wood_light')
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
    g.beam('Axe handle',(-1.34,-1.44,.45),(-1.08,-1.39,1.04),.07,.065,'wood_light',.01)
    g.mesh('Axe iron head',[(-1.29,-1.37,.94),(-.86,-1.37,.89),(-.82,-1.37,1.14),(-1.24,-1.37,1.10),
                            (-1.29,-1.44,.94),(-.86,-1.44,.89),(-.82,-1.44,1.14),(-1.24,-1.44,1.10)],
           [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'silver',.02)
    for i in range(4): g.stepping_stone((.30+(i%2)*.10,-1.18-i*.27),.21)
    g.shrub((.68,-.25,2.77),.25)
    for a,b in [((1.86,.23,0),(1.86,1.48,0)),((.8,1.7,0),(1.75,1.7,0))]: g.fence(a,b,3,.60)


def bakery():
    cottage_body(True); roof('red'); chimney(.66,.51)
    # The door opening sits behind the market canopy; warm loaves read at game distance.
    arch('Bakery oven opening',.46,-.972,.20,.78,1.13,'shadow')
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
    for i in range(5):
        x=.06+i*.24; y=-1.52+(.07 if i%2 else -.04)
        loaf=g.ico('Golden bread loaf',(x,y,.79),(.16,.12,.11),'gold',2,.035)
        for j in range(3):
            g.beam('Bread score',(x-.07+j*.07,y-.065,.864),(x-.07+j*.07,y+.05,.885),.024,.015,'cream',.005)
    for i in range(3): g.ico('Oven bread loaf',(.25+i*.19,-1.02,.33),(.13,.11,.09),'gold',2)
    g.barrel((-1.25,-.72,0),1.15); g.crate((-1.03,-1.42,0),.43)
    g.cube('Bakery sign post',(-1.13,.02,1.88),(.14,.16,3.50),'wood_light')
    g.beam('Bakery hanging sign beam',(-1.65,-.04,3.32),(-.12,-.04,3.32),.18,.16,'wood_edge')
    for x in [-1.58,-1.04]: g.tube('Sign chain',[(x,-.04,3.23),(x,-.04,2.95)],.015,'silver_dark',6)
    g.cube('Bakery wooden sign',(-1.31,-.05,2.64),(.81,.14,.58),'wood_light',.12)
    g.ico('Bread sign emblem',(-1.31,-.139,2.64),(.25,.025,.12),'gold_light',2,.02)
    for x in [-1.43,-1.31,-1.19]: g.beam('Bread emblem cuts',(x,-.17,2.60),(x+.035,-.17,2.70),.028,.022,'cream',.003)
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
    for i in range(11):
        x=cx+g.RNG.uniform(-.33,.33); y=cy+g.RNG.uniform(-.29,.29)
        g.ico('Cart gold ore',(x,y,.93+g.RNG.uniform(0,.11)),(.15,.14,.14),g.RNG.choice(['gold','gold_light']),1)
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
    for x in [-.91,-.45,0,.45,.91]: g.cube('Balcony railing post',(x,-1.19,2.10),(.105,.105,.53),'wood_light',.015)
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
    g.mesh('Blue treehouse banner',[(.46,-1.255,1.88),(.91,-1.255,1.88),(.91,-1.30,1.01),
                                  (.69,-1.30,1.16),(.46,-1.30,1.01)],[(0,1,2,3,4)],'blue')
    for a,b in [((.69,-1.313,1.28),(.69,-1.313,1.73)),((.69,-1.313,1.54),(.58,-1.313,1.65)),
                ((.69,-1.313,1.48),(.81,-1.313,1.61))]: g.beam('Banner white tree emblem',a,b,.022,.014,'cream',0)
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
