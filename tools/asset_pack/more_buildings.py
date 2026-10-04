"""Five reference buildings assembled from the village's shared architectural kit."""
import math
import geometry as g
import buildings as cottage
import autobattler_buildings as village
import village_kit as kit


def entrance(x=0, y=-.95, z=.12):
    cottage.door(x,y,z,.64,1.38)
    village.stone_arch(x,y-.025,z,.64,1.38)
    village.stairs(x,y-.67,z+.08,3,.91)


def flag(pos):
    x,y,z=pos
    g.beam('Flagstaff',(x,y,z),(x,y,z+.64),.055,.055,'wood_light')
    g.mesh('Blue civic pennant',[(x,y,z+.62),(x+.55,y-.03,z+.56),(x+.42,y,z+.28),(x,y,z+.30)],[(0,1,2,3)],'blue')


def archery_range():
    village.cottage_shell(); entrance(); village.dormer((-.68,-.28,2.48))
    village.group('Elevated archery lookout',lambda: lookout(),(1.12,.62,0),.72)
    village.canopy(1.23,-.25,1.96,1.25,.96)
    kit.place('target',(1.45,-1.25,0),1.36,(0,0,-.17))
    kit.place('open_barrel',(-1.43,-.87,0),1.0)
    for i in range(5):kit.place('arrow',(-1.55+i*.06,-.89,1.21),1.04,(math.pi,(i-2)*.12,0))
    for x in [-1.79,-1.02]:g.cube('Arrow rack upright',(x,-1.15,.59),(.085,.085,1.18),'wood_light')
    for z in [.30,.78]:g.beam('Arrow rack tie',(-1.79,-1.15,z),(-1.02,-1.15,z),.075,.075)
    for i in range(4):kit.place('arrow',(-1.68+i*.17,-1.23,1.50),1.28,(math.pi,.10,0))
    village.banner((.35,-1.22,3.03),'arrow',.69,1.26)
    # Broad bow emblem above the arrow so the role reads from a distance.
    g.tube('Archery bow emblem',[(.12,-1.33,2.40),(.46,-1.33,2.65),(.12,-1.33,2.94)],.025,'cream',8)
    g.beam('Bow emblem string',(.12,-1.33,2.40),(.12,-1.33,2.94),.012,.012,'cream',0)
    village.lantern_arm((-1.1,-.93,1.93));village.dress();village.front_path()


def lookout():
    village.masonry(.82,.82,2.4)
    for x in [-.5,.5]:
        for y in [-.5,.5]:g.cube('Lookout upright',(x,y,3.02),(.17,.17,1.4),'wood_light')
    for i in range(5):g.cube('Lookout deck plank',(-.48+i*.24,0,2.49),(.23,1.18,.14),'wood_light')
    for y in [-.57,.57]:
        for z in [2.65,2.91]:g.beam('Lookout rail',(-.58,y,z),(.58,y,z),.13,.12,'wood_edge')
    village.hip_roof(3.68,.72,.52);flag((0,0,4.21))


def research_tower():
    village.group('Observatory cottage',lambda: observatory_cottage(),(-.67,-.18,0),.78)
    village.group('Round observatory tower',observatory,(.63,.46,0))
    village.table((-.94,-1.23,0),1.07,.65,.70)
    g.cube('Observatory parchment',(-.94,-1.23,.77),(.90,.58,.035),'cream',.01)
    for r in [.12,.23]:g.torus('Chart orbit',(-.94,-1.23,.794),r,.009,'wood',sides=24)
    for i in range(3):kit.place('book',(-1.58,-.26,.08+i*.14),.9)
    kit.place('crate',(1.40,-.72,0),1.05)
    for x,r in [(1.26,.15),(1.58,.11)]:
        g.lathe('Glass alchemical flask',[(0,r),(.18,r),(.25,r*.36),(.37,r*.33)],'blue_light',12,(x,-.72,.51))
    g.torus('Armillary outer orbit',(1.33,-.52,1.07),.34,.032,'gold','Y',24)
    g.torus('Armillary tilted orbit',(1.33,-.52,1.07),.27,.026,'gold','X',24)
    g.beam('Armillary stand',(1.33,-.52,.50),(1.33,-.52,.91),.085,.085,'gold')
    village.dress();village.front_path()


def observatory_cottage():
    village.cottage_shell(); entrance();village.dormer((-.65,-.1,2.45));cottage.chimney(-.64,.62)
    village.lantern_arm((-1.07,-.95,1.98))


def observatory():
    g.lathe('Observatory round limestone walls',[(0,.74),(3.05,.74)],'wall',16)
    for z in [.16,1.0,1.83,2.68]:g.torus('Round tower stone course',(0,0,z),.75,.055,'wall_light',sides=16)
    for i in range(8):
        a=i*math.tau/8;g.beam('Round tower timber upright',(.76*math.cos(a),.76*math.sin(a),.15),(.76*math.cos(a),.76*math.sin(a),3.04),.14,.14,'wood_light')
    cottage.window(0,-.775,1.38,.43,1.13)
    g.lathe('Blue observatory dome',[(0,.94),(.24,.89),(.48,.74),(.69,.52),(.83,.25),(.88,.04)],'roof_blue',16,(0,0,3.03))
    for i in range(8):
        a=i*math.tau/8
        g.tube('Dome brass rib',[(r*math.cos(a),r*math.sin(a),3.04+z) for z,r in [(0,.95),(.24,.90),(.48,.75),(.69,.53),(.84,.25),(.90,.03)]],.04,'gold',6)
    for z,r in [(3.27,.89),(3.51,.74)]:g.torus('Dome shingle course',(0,0,z),r,.017,'roof_blue_dark',sides=32)
    g.lathe('Dome eave brass collar',[(0,.97),(.12,.97)],'gold',16,(0,0,2.96))
    # Visible barrel, lens and fork; angled toward the sky.
    a=(.22,-.08,3.54);b=(1.55,-.38,4.21)
    g.tube('Telescope dark barrel',[a,b],[.21,.25],'wood_dark',16)
    for t in [0,.25,.72,1]:
        p=tuple(a[i]+(b[i]-a[i])*t for i in range(3));q=tuple(p[i]+(b[i]-a[i])*.05 for i in range(3))
        g.tube('Brass telescope band',[p,q],.27,'gold',16,caps=False)
    tip=tuple(b[i]+(b[i]-a[i])*.052 for i in range(3))
    g.tube('Blue telescope lens',[tip,tuple(v+.005*(b[i]-a[i]) for i,v in enumerate(tip))],.215,'blue_light',24)
    g.beam('Telescope fork',(.53,-.15,3.13),(.53,-.15,3.69),.12,.12,'gold')
    village.banner((-.40,-.87,3.10),'eye',.62,1.03)


def metal_mine():
    village.group('Mine office',lambda: mine_office(),(-.85,-.05,0),.76)
    for x,y,z,s in [(0,.40,1.35,.83),(.57,.74,1.45,1.0),(1.08,.57,1.15,.76),(.68,1.03,2.25,.7)]:
        ob=g.ico('Angular mine outcrop',(x,y,z),(s,.73*s,1.12*s),'stone',1,.14);g.facet_colors(ob,['stone','stone_light','stone_dark'])
    g.cube('Mine tunnel darkness',(.65,-.33,.79),(1.06,.18,1.35),'shadow',.03)
    for x in [.06,1.27]:g.cube('Mine entrance timber', (x,-.45,.85),(.21,.25,1.70),'wood_light')
    g.beam('Mine lintel',(-.06,-.45,1.65),(1.4,-.45,1.65),.24,.26,'wood_edge')
    kit.place('lantern',(.82,-.56,1.12),.84)
    for x in [.30,.96]:g.beam('Cart iron rail',(x,-1.85,.045),(x,-.3,.045),.065,.065,'iron',.006)
    for i in range(7):g.cube('Rail sleeper',(.63,-1.70+i*.21,.022),(1.02,.11,.05),'wood_dark',.004)
    village.group('Loaded mine cart',mine_cart,(.63,-1.09,.05),.91)
    g.cube('Ore hoist upright',(1.68,.47,1.68),(.24,.26,3.36),'wood_light')
    g.beam('Ore hoist arm',(1.04,.47,3.26),(2.03,.47,3.26),.25,.24,'wood_edge')
    g.torus('Hoist pulley',(1.96,.47,3.14),.13,.035,'iron','Y')
    g.tube('Hoist rope',[(1.96,.47,3.14),(1.96,.47,2.22)],.022,'rope')
    kit.place('crate',(1.96,.47,1.77),.72)
    for s in [-1,1]:g.beam('Crate sling',(1.96+s*.16,.47,2.12),(1.96,.47,2.34),.025,.025,'rope',0)
    village.banner((-.34,-1.02,2.59),'blank',.65,1.01)
    for s in [-1,1]:
        g.beam('Crossed pick shaft',(-.34+s*.19,-1.13,1.91),(-.34-s*.19,-1.13,2.42),.035,.035,'cream',.004)
        g.beam('Pick blade',(-.34-s*.32,-1.13,2.36),(-.34-s*.04,-1.13,2.53),.05,.045,'cream',.008)
    kit.place('crate',(-1.22,-1.29,0),.84)
    for i in range(4):g.ico('Stacked iron ingot',(-1.31+(i%2)*.2,-1.3,.46+(i//2)*.10),(.15,.12,.07),'silver_dark',1,0)
    village.dress()


def mine_office():
    village.cottage_shell();cottage.window(-.22,-.95,.48,.54,.93);cottage.chimney(-.65,.57)


def mine_cart():
    kit.place('open_crate',(0,0,.26),1.3)
    for x in [-.28,.28]:
        for y in [-.31,.31]:
            g.tube('Mine cart iron wheel',[(x,y-.05,.22),(x,y+.05,.22)],.19,'iron',12)
            g.tube('Mine cart axle',[(x,y-.06,.22),(x,y+.06,.22)],.052,'silver',8)
    for i in range(5):g.ico('Iron ore load',((i%2-.5)*.23,(i//2-1)*.18,.88),(.20,.17,.15),'silver_dark',1)


def weaver():
    village.cottage_shell();entrance(-.43);cottage.chimney(.62,.54);village.dormer((-.68,-.23,2.45))
    village.group('Blue linen striped work awning',lambda:village.canopy(0,0,0,1.53,.87,True),(.59,-.87,2.13))
    # Override the existing striped canopy palette at object level.
    for obj in g.CURRENT.objects:
        if obj.name.startswith('Canvas canopy stripe'):
            for slot in obj.material_slots:
                if slot.material==g.M['red']:slot.link='OBJECT';slot.material=g.M['blue']
    village.group('Working loom',loom,(.71,-1.53,0),.88)
    village.table((-1.36,-.88,0),.68,.52,.63)
    for i,mat in enumerate(['blue','red','cream']):g.cube('Folded fabric',(-1.36,-.88,.73+i*.085),(.53,.41,.085),mat,.02)
    for x,y in [(1.56,-.75),(1.28,.05)]:
        kit.place('open_barrel',(x,y,0),.72)
        for j,mat in enumerate(['red','blue','cream']):g.lathe('Dyed cloth roll',[(0,.085),(.57,.085)],mat,10,(x+(j-1)*.12,y,.33))
    village.banner((1.50,-.30,3.05),'blank',.73,1.14)
    for s in [-1,1]:
        for i in [-1,0,1]:g.beam('Woven cloth sign', (1.5+i*.10-s*.18,-.43,2.34),(1.5+i*.10+s*.18,-.43,2.71),.029,.023,'cream',.004)
    village.lantern_arm((-1.16,-.94,1.99));village.dress();village.front_path()


def loom():
    for x in [-.54,.54]:
        for y in [-.30,.30]:g.cube('Loom upright',(x,y,.61),(.085,.085,1.22),'wood_light')
    for z in [.35,1.12]:g.beam('Loom beam',(-.60,-.30,z),(.60,-.30,z),.10,.10,'wood_edge')
    for i in range(16):
        x=-.48+i*.064
        g.tube('Loom warp thread',[(x,-.31,1.07),(x,-.44,.66),(x,-.58,.57)],.009,'cream',4)
    for i in range(8):g.cube('Woven striped cloth',(-.44+i*.126,-.48,.60),(.12,.40,.035),'blue' if i%2==0 else 'cream',.006)
    for x in [-.55,.55]:g.tube('Cloth beam axle',[(x,-.5,.56),(x,-.6,.56)],.07,'wood_edge',8)
    g.beam('Loom shuttle',(-.23,-.43,.68),(.15,-.43,.68),.035,.04,'gold',.005)


def town_hall():
    village.group('Town hall left wing',lambda:hall_wing(),(-1.12,.28,0),(.62,.85,.88))
    village.group('Town hall right wing',lambda:hall_wing(),(1.12,.28,0),(.62,.85,.88))
    village.group('Town hall central portal',lambda:hall_center(),(0,-.30,.25),(.74,.86,1.0))
    village.stairs(0,-1.84,.46,4,1.27)
    village.group('Civic bell tower',bell_tower,(0,.26,2.88),.91)
    village.shield_emblem((0,-1.50,2.90),.84,'blank')
    g.cube('Crown emblem base',(0,-1.63,2.85),(.58,.06,.075),'gold',.012)
    for dx in [-.25,0,.25]:g.beam('Crown emblem prong',(dx,-1.63,2.85),(dx*1.2,-1.63,3.07 if dx else 3.15),.06,.05,'gold')
    for x in [-1.0,1.0]:village.banner((x,-.83,2.80),'blank',.42,1.22)
    for x in [-.79,.79]:kit.place('lantern',(x,-1.31,.64),.82)
    kit.place('bench',(-1.26,-1.28,0),.8)
    g.cube('Civic notice board',(-1.81,-.82,1.11),(.79,.15,.75),'wood_light',.05)
    for x in [-2.07,-1.56]:g.cube('Notice board post',(x,-.8,.61),(.09,.09,1.22),'wood')
    for x,z in [(-2.01,1.20),(-1.76,1.06),(-1.61,1.30)]:g.cube('Pinned town notice',(x,-.91,z),(.19,.018,.24),'cream',.005)
    village.dress();village.front_path()


def hall_wing():
    village.cottage_shell();cottage.window(0,-.96,.43,.67,1.12);village.dormer((.68,-.22,2.49))


def hall_center():
    village.cottage_shell();entrance();cottage.window(0,-.95,2.28,.40,.53)


def bell_tower():
    village.masonry(.75,.74,.83)
    for x in [-.42,.42]:
        for y in [-.42,.42]:g.cube('Bell tower post',(x,y,1.18),(.12,.12,.78),'wood_light')
    g.lathe('Golden civic bell',[(0,.26),(.07,.27),(.12,.20),(.42,.14),(.49,.045)],'gold',16,(0,0,.86))
    g.ico('Bell clapper',(0,0,.83),(.055,.055,.09),'gold_light',2)
    g.beam('Bell suspension',(0,0,1.29),(0,0,1.56),.05,.05,'iron')
    village.hip_roof(1.53,.62,.55);flag((0,0,2.11))


BUILDERS={'archery_range':archery_range,'research_tower':research_tower,
          'metal_mine':metal_mine,'weaver':weaver,'town_hall':town_hall}


def details(name):
    """Role-specific second pass without changing the reference silhouette."""
    if name=='archery_range':
        for i in range(3):kit.place('arrow',(1.32+i*.13,-2.14,.90+i*.08),.82,(-math.pi/2,0,-.09+i*.07))
        for x in [-1.69,-1.13]:
            g.tube('Arrow rack peg',[(x,-1.17,.78),(x,-1.21,.78)],.026,'iron',8)
        for y in [-.35,.0,.35]:
            g.cube('Lookout deck iron strap',(1.12,.62+y,1.81),(.56,.035,.023),'iron',.004)
    elif name=='research_tower':
        for angle in [.2,1.2,2.1,3.5,4.8]:
            x=-.94+.19*math.cos(angle);y=-1.23+.19*math.sin(angle)
            g.ico('Chart star marking',(x,y,.798),(.014,.014,.002),'wood_dark',1,0)
        for i in range(4):g.beam('Chart handwritten notes',(-1.30,-1.06+i*.043,.799),(-1.16+(i%2)*.08,-1.06+i*.043,.799),.006,.005,'wood_dark',0)
        for x in [1.26,1.58]:
            g.lathe('Flask stopper',[(0,.036),(.09,.036)],'wood_edge',8,(x,-.72,.83))
        for i in range(3):kit.place('book',(-1.52,-.24,.16+i*.11),.75,(0,0,.18*i))
        g.tube('Telescope polished lens rim',[(2.257,.0626,4.249),(2.2703,.0596,4.2557)],.219,'gold_light',24,caps=False)
    elif name=='metal_mine':
        for x in [.34,.92]:
            for y in [-1.36,-.84]:
                g.cube('Mine cart iron corner strap',(x,y,.52),(.045,.047,.50),'iron',.007)
                for z in [.38,.62]:g.ico('Mine cart strap rivet',(x,y-.03,z),(.025,.014,.025),'silver',2,0)
        g.beam('Resting miner pick shaft',(-.58,-1.03,.05),(-.27,-1.03,1.20),.06,.06,'wood_light',.01)
        g.tube('Curved miner pick blade',[(-.59,-1.03,1.04),(-.32,-1.03,1.18),(-.03,-1.03,1.08)],.052,'silver',8)
        for i in range(3):g.cube('Ore ingot polished top',(-1.33+i*.13,-1.30,.71),(.12,.18,.045),'silver',.008)
    elif name=='weaver':
        for i in range(7):
            x=.36+i*.105
            g.tube('Fine woven cloth stripe',[(x,-1.78,.56),(x,-1.74,.59),(x,-1.60,.59)],.005,'blue_dark',4)
        for x,mat in [(-1.50,'blue'),(-1.31,'red'),(-1.12,'cream')]:
            g.lathe('Thread spool',[(0,.048),(.15,.048)],mat,12,(x,-.83,1.04))
            for z in [1.04,1.19]:g.lathe('Thread spool wooden end',[(0,.063),(.015,.063)],'wood_edge',12,(x,-.83,z))
        for x in [1.02,1.15]:g.lathe('Weaver dye jar',[(0,.07),(.15,.07),(.18,.046)],'blue',12,(x,-1.50,.58))
    elif name=='town_hall':
        for x in [-2.01,-1.76,-1.61]:
            z=1.20 if x==-2.01 else 1.06 if x==-1.76 else 1.30
            for i in range(3):g.beam('Written civic notice',(x-.06,-.925,z-.07+i*.045),(x+.055,-.925,z-.07+i*.045),.007,.005,'wood_dark',0)
            g.ico('Notice tack',(x,-.93,z+.084),(.012,.008,.012),'gold',2,0)
        for x in [-1,1]:
            # A simple fleur-de-lis covers the old sword's pointed silhouette.
            for s in [-1,1]:g.tube('Civic fleur side petal',[(x,-.98,2.24),(x+s*.09,-.98,2.36),(x+s*.10,-.98,2.43),(x+s*.035,-.98,2.40)],.024,'cream',8)
        for x in [-.24,0,.24]:g.ico('Crown jewel',(x,-1.67,3.035 if x else 3.12),(.037,.02,.037),'gold_light',2,0)
