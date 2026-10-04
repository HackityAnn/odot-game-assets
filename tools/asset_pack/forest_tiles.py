"""Eight ready-to-place hex tiles assembled from independently reusable components."""
import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
from mathutils import Vector
import geometry as g
import reference_finish as finish
import painted_finish as paint
import art_style as style
import forest_kit as kit
from catalog import BY_ID

# Recipes carry composition only; all geometry lives in the component library.
RECIPES={
 'hex_crystal_grove':[
  ('crystal_blue',(.05,.46,0),1.92),('crystal_blue',(-.60,-.42,0),.85),
  ('crystal_purple',(.78,.31,0),1.0),('crystal_blue',(-.29,-.89,0),.48),
  ('rune_monolith',(-1.03,.48,0),1.03),('rune_monolith',(.84,-.78,0),.67),
  ('mushroom_blue',(-1.38,-.54,0),.53),('mushroom_purple',(1.41,.10,0),.39),
  ('boulder',(.27,-.16,0),.98),('boulder',(.67,-.46,0),.71)],
 'hex_mystical_grove':[
  ('crystal_blue',(.04,.65,0),1.96),('crystal_blue',(-.77,.36,0),1.10),
  ('crystal_blue',(.91,.51,0),1.24),('crystal_purple',(.11,-.91,0),.51),
  ('boulder',(-.10,-.06,0),1.52),('boulder',(-.59,-.73,0),1.11),
  ('boulder',(.81,-.40,0),1.07),('mushroom_blue',(-1.27,-.33,0),.59),
  ('mushroom_blue',(1.30,-.64,0),.42),('mushroom_purple',(-1.49,-.67,0),.32)],
 'hex_rune_shrine':[
  ('rune_monolith',(0,.77,0),1.68),('rune_monolith',(-1.02,.41,0),.92),
  ('rune_monolith',(1.01,.47,0),1.13),('shrine_plinth',(0,-.20,0),1),
  ('rune_circle',(0,-.20,.354),1),('lantern_post',(-1.60,.61,0),1),
  ('lantern_post',(1.48,.61,0),.88),('mushroom_blue',(-.99,-.73,0),.70),
  ('crystal_blue',(1.42,-.46,0),.66),('crystal_blue',(-1.48,-.62,0),.53),
  ('boulder',(-.20,-1.15,0),.79),('boulder',(.67,-.89,0),.62)],
 'hex_glowing_mushrooms':[
  ('mushroom_blue',(-.40,.52,0),1.60),('mushroom_purple',(.95,.19,0),1.11),
  ('mushroom_blue',(-1.09,-.73,0),.66),('mushroom_purple',(.16,-1.12,0),.56),
  ('crystal_blue',(1.35,-.72,0),.62),('crystal_purple',(1.57,-.51,0),.46),
  ('boulder',(-.21,-.46,0),.88),('boulder',(-1.37,-.89,0),.67)],
 'hex_bioluminescent_grove':[
  ('tree_snag',(-.35,.16,0),1.30),('mushroom_purple',(-.35,.16,1.33),1.46),
  ('mushroom_blue',(1.01,.12,0),1.09),('mushroom_purple',(-1.23,-.17,0),.67),
  ('mushroom_blue',(.47,-1.06,0),.50),('root',(-.27,-.19,0),1.3),
  ('crystal_blue',(-1.4,-.74,0),.56),('boulder',(-.88,-1.02,0),.68),
  ('boulder',(.91,-.67,0),.53)],
 'hex_crystal_shrine':[
  ('shrine_plinth',(0,-.08,0),1.10),('rune_circle',(0,-.08,.393),1.05),
  ('crystal_blue',(0,-.08,.93),.79),('rune_diamond',(0,-.27,1.26),.75),
  ('crystal_blue',(-1.22,.0,0),1.03),('crystal_purple',(-.73,1.12,0),1.20),
  ('crystal_blue',(.56,1.20,0),1.13),('crystal_purple',(1.25,.20,0),.90),
  ('crystal_blue',(.98,-.83,0),.54),('crystal_blue',(-.93,-.92,0),.48),
  ('boulder',(-.86,.59,0),.96),('boulder',(.90,.75,0),1.22),
  ('mushroom_blue',(-1.49,-.64,0),.42),('mushroom_purple',(1.42,-.51,0),.36)],
 'hex_lantern_bridge':[], 'hex_woodland_bridge':[],
}


def dress(stream=False):
    # Fixed placements remain within the shared hex footprint and off the channel.
    for i,(x,y) in enumerate([(-1.85,-.48),(-1.28,1.37),(1.63,.62),(1.22,-1.26),(-1.06,-1.45),(1.70,-.29)]):
        kit.place('leaf_clump',(x,y,0),.68+(i%3)*.12,(0,0,i*.81))
        kit.place('moss',(x+.09,y+.05,.025),.85)
        if i%2==0:kit.place('boulder',(x*.94,y*.95,0),.38)
        if i%2:kit.place('mushroom_small',(x-.12,y-.17,0),.82)
        else:g.flower((x+.18,y-.16,.02),.75)
    for i,(x,y) in enumerate([(-1.43,.13),(1.12,-1.17),(-.8,-1.53)]):
        kit.place('fern',(x,y,0),.79,(0,0,i*1.2))
    if not stream:
        for x,y,s in [(-.78,-.08,.7),(.65,.82,.62),(.49,-.67,.57)]:kit.place('leaf_clump',(x,y,0),s)
    for i in range(18):
        a=i*2.399963+.17;r=1.48+.28*math.sin(i*1.13)
        x,y=r*math.cos(a),r*math.sin(a)
        if stream and abs(x)<.68:continue
        kit.place('moss',(x,y,.005),(.95,.82,.60))
        kit.place('leaf_clump',(x+.09,y-.04,0),.42+.09*math.sin(i),(0,0,a))
    # Small varied blades add detail between broad leaves without a regular border.
    vertices=[];faces=[]
    for i in range(54):
        a=i*2.399963;r=.86+.90*(.5+.5*math.sin(i*1.71))
        x,y=r*math.cos(a),r*math.sin(a)
        if stream and abs(x)<.69:continue
        for j in range(3):
            angle=a+j*2.1;h=.07+.035*math.sin(i+j)**2
            dx,dy=.024*math.cos(angle),.024*math.sin(angle)
            n=len(vertices)
            vertices.extend([(x-dy,y+dx,.007),(x+dy,y-dx,.007),(x+dx*1.2,y+dy*1.2,h)])
            faces.append((n,n+1,n+2))
    tuft=g.mesh('Fine scattered woodland grasses',vertices,faces,'forest_leaf_light')
    uv=tuft.data.uv_layers.new(name=style.TEXTURES.uv_name)
    for poly in tuft.data.polygons:
        for index,coord in zip(poly.loop_indices,[(0,0),(1,0),(.5,1)],strict=True):uv.data[index].uv=coord


def climbing_growth(root,kind):
    if kind not in ['rune_monolith','tree_snag','boulder']:return
    for i,z in enumerate([.28,.65,1.04] if kind!='boulder' else [.43]):
        moss=kit.place('moss');moss.parent=root
        moss.location=Vector(((-1 if i%2 else 1)*.29,-.02,z))
        moss.scale=(.53,.57,.47)
        leaves=kit.place('leaf_clump');leaves.parent=root
        leaves.location=moss.location+Vector((.0,-.07,.02));leaves.scale=(.33,)*3
        leaves.rotation_euler=(0,.75,i*1.3)


def bridge(stone):
    # River runs along Y. The deck crosses X with a clear underside arch.
    for x in [-.84,.84]:
        if stone:
            for y in [-.49,.49]:
                for z in [.0,.22]:kit.place('stone_block',(x,y,z),(1.8,1.7,1.0))
        else:
            for y in [-.43,.43]:kit.place('bridge_post',(x,y,.30),1)
    if stone:
        for y in [-.40,.40]:
            for i in range(11):
                a=(i-5)*math.pi/11
                kit.place('stone_arch_block',(0,y,-.14),1,(0,a,0))
        for i in range(13):
            x=-1.03+i*.172;z=.32+.38*math.sqrt(max(0,1-(x/1.15)**2))
            for y in [-.36,-.12,.12,.36]:kit.place('stone_block',(x,y,z),(.59,.93,.43))
        for y in [-.57,.57]:
            for i in range(10):
                x=-.98+i*.218;z=.40+.38*math.sqrt(max(0,1-(x/1.15)**2))
                kit.place('stone_block',(x,y,z),(.71,.64,.74))
        for x in [-.97,.97]:
            for y in [-.56,.56]:
                for z in [.24,.48,.72]:kit.place('stone_block',(x,y,z),(1,1,1))
                kit.place('moss',(x,y,1.0),.74)
    else:
        for i in range(15):
            x=-1.12+i*.16;z=.27+.31*math.sqrt(max(0,1-(x/1.20)**2))
            slope=-.31*x/(1.20**2*math.sqrt(max(.08,1-(x/1.20)**2)))
            kit.place('bridge_plank',(x,0,z),1,(0,-math.atan(slope),0))
        for y in [-.48,.48]:
            g.tube('Arched wooden stringer',[(-1.18,y,.20),(-.60,y,.44),(0,y,.53),(.60,y,.44),(1.18,y,.20)],.09,'wood',8)
            for z in [.67,.97]:
                kit.place('bridge_rail',(-.43,y,z),(.86,1,1),(0,-.08,0))
                kit.place('bridge_rail',(.43,y,z),(.86,1,1),(0,.08,0))
    for x,y in [(-1.20,.82),(1.10,.81)]:kit.place('lantern_post',(x,y,0),.93)
    # Rocky cascades use the same channel base and reusable water/foam meshes.
    for i,(x,y) in enumerate([(-.69,-1.28),(.69,-1.29),(-.63,.96),(.64,1.39),(-.77,-.71),(.76,-.63)]):
        kit.place('boulder',(x,y,-.13),.72+(i%2)*.18)
        kit.place('moss',(x,y,.28),.75)
    kit.place('waterfall',(0,-1.16,.13),(.92,1,.62))
    for y in [-1.52,-1.97,.93]:kit.place('foam',(0,y,-.16),1.05)
    kit.place('mushroom_blue',(-1.25,-.86,0),.48)
    kit.place('mushroom_purple',(1.54,.32,0),.40)
    kit.place('crystal_blue',(1.34,.74,0),.56)
    kit.place('leaf_clump',(-.8,.13,.75),.68)


def build_one(name,render=True):
    if name not in RECIPES:raise ValueError(name)
    g.clear_scene();kit.reset()
    asset=g.collection(name);g.target(asset);root=g.empty(name+'_root')
    stream=name in ['hex_lantern_bridge','hex_woodland_bridge']
    kit.place('hex_stream' if stream else 'hex_meadow')
    for kind,pos,scale in RECIPES[name]:
        climbing_growth(kit.place(kind,pos,scale),kind)
        if kind in ['boulder','rune_monolith']:
            kit.place('leaf_clump',(pos[0]-.23*scale,pos[1]-.24*scale,.025),.55*scale,(0,0,pos[0]*2))
            kit.place('moss',(pos[0]+.24*scale,pos[1]-.20*scale,.015),(.72*scale,.6*scale,.5*scale))
    if stream:bridge(name=='hex_lantern_bridge')
    dress(stream);g.attach_all(asset,root)
    root['asset_role']=name;root['hex_radius']=kit.RADIUS;root['hex_orientation']='flat_top'
    root['ground_origin']='meadow surface z=0; foundation bottom=-0.36'
    root['grid_spacing_x']=style.HEX.spacing_x;root['grid_spacing_y']=style.HEX.spacing_y
    root['reference']='sources/reference/'+BY_ID[name]['reference']
    root['kit_source']='sources/environment/shared_forest_kit.blend'
    root['river_connections']='north,south' if stream else ''
    root['modeling_stage']='reference_detail_pass'
    asset.asset_mark();asset.asset_data.description='Complete magical forest hex tile: '+BY_ID[name]['title']
    image=bpy.data.images.load(str(g.ROOT/root['reference']),check_existing=True);image.pack();image.use_fake_user=True
    finish.palette()
    paint.apply(asset)
    paint.ground(asset,name)
    root['modeling_stage']=paint.VERSION
    g.studio(1.05,6.65);finish.studio_finish()
    scene=bpy.context.scene;scene.name=name
    scene.render.filepath=str(g.ROOT/'exports/previews'/f'{name}.png')
    path=g.ROOT/'sources/environment'/f'{name}.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    if render:bpy.ops.render.render(write_still=True)
    print('Saved tile:',name,'with',len(asset.objects),'objects',flush=True)


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(RECIPES)
    for name in [a for a in args if a!='--no-render'] or list(RECIPES):
        build_one(name,'--no-render' not in args)
