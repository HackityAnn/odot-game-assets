"""Original, editable geometry for the supplied fantasy village reference."""
import math
import random
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
RNG = random.Random(407)
M = {}
CURRENT = None


def enum(owner, prop, value):
    choices = {item.identifier for item in owner.bl_rna.properties[prop].enum_items}
    if value not in choices:
        raise ValueError(f"{prop}: {value!r} not in {choices}")
    setattr(owner, prop, value)


def material(name, rgb, roughness=.8, metal=0, emission=0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    # Palette values are sRGB; convert to scene-linear for consistent renders.
    linear = tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in rgb)
    shader.inputs['Base Color'].default_value = (*linear, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metal
    shader.inputs['Emission Color'].default_value = (*linear, 1)
    shader.inputs['Emission Strength'].default_value = emission
    mat.diffuse_color = (*linear, 1)
    M[name] = mat
    return mat


def palette():
    colors = {
        'wood': (.43,.245,.115), 'wood_light': (.64,.385,.19),
        'wood_edge': (.73,.47,.255), 'wood_dark': (.255,.145,.085),
        'bark': (.40,.205,.095), 'bark_light': (.51,.285,.115),
        'stone': (.54,.54,.51), 'stone_light': (.66,.65,.59),
        'stone_dark': (.39,.41,.40), 'wall': (.81,.76,.62),
        'wall_light': (.90,.85,.72), 'shadow': (.105,.075,.07),
        'grass': (.54,.68,.20), 'grass_light': (.67,.76,.28),
        'grass_dark': (.36,.51,.125), 'leaf': (.40,.60,.14),
        'leaf_light': (.57,.72,.18), 'leaf_dark': (.28,.44,.105),
        'pine': (.25,.43,.14), 'pine_light': (.34,.52,.18),
        'soil': (.29,.28,.235), 'base': (.28,.29,.29),
        'roof_red': (.74,.255,.125), 'roof_red_light': (.87,.36,.18),
        'roof_red_dark': (.61,.18,.09), 'roof_blue': (.19,.39,.55),
        'roof_blue_light': (.29,.49,.66), 'roof_blue_dark': (.13,.29,.43),
        'blue': (.15,.34,.75), 'blue_light': (.25,.47,.94),
        'blue_dark': (.09,.20,.48), 'purple': (.40,.18,.62),
        'purple_light': (.58,.30,.78), 'purple_dark': (.24,.11,.39),
        'green': (.29,.48,.14), 'green_light': (.42,.62,.20),
        'green_dark': (.17,.33,.09), 'skin': (.96,.69,.35),
        'skin_light': (1,.78,.47), 'leather': (.34,.205,.115),
        'leather_light': (.46,.29,.16), 'silver': (.70,.74,.79),
        'silver_light': (.88,.89,.87), 'silver_dark': (.40,.45,.50),
        'gold': (.96,.65,.15), 'gold_light': (1,.79,.30),
        'cream': (.99,.92,.73), 'red': (.82,.18,.11),
        'mushroom': (.55,.23,.83), 'black': (.07,.047,.04),
        'face_dark': (.19,.095,.24), 'flower': (.94,.88,.73),
        'window': (1,.64,.075), 'magic': (.86,.19,1),
    }
    for name, color in colors.items():
        material(name, color, roughness=.42 if name.startswith('silver') else .78,
                 metal=.35 if name.startswith('silver') else .10 if name.startswith('gold') else 0,
                 emission=1.5 if name == 'window' else 2.5 if name == 'magic' else 0)


def collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def target(col):
    global CURRENT
    CURRENT = col


def mesh(name, verts, faces, mat, bevel=0):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    CURRENT.objects.link(obj)
    data.materials.append(M[mat] if isinstance(mat, str) else mat)
    if bevel:
        mod = obj.modifiers.new('Soft carved edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return obj


def cube(name, pos, size, mat, bevel=.025, rot=None):
    transform = Matrix.Translation(Vector(pos))
    if rot is not None:
        from mathutils import Euler
        transform @= Euler(rot).to_matrix().to_4x4()
    verts = [transform @ Vector((x*size[0]/2,y*size[1]/2,z*size[2]/2))
             for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),
                           (1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
    return mesh(name, verts, [(0,4,6,2),(1,3,7,5),(0,1,5,4),
                              (2,6,7,3),(0,2,3,1),(4,5,7,6)], mat, bevel)


def ico(name, pos, size, mat, subdivisions=1, irregular=.06):
    data = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1)
    for vertex in bm.verts:
        jitter = 1 + RNG.uniform(-irregular, irregular)
        vertex.co = Vector(pos) + Vector(tuple(vertex.co[i]*size[i]*jitter for i in range(3)))
    bm.to_mesh(data)
    bm.free()
    obj = bpy.data.objects.new(name, data)
    CURRENT.objects.link(obj)
    data.materials.append(M[mat])
    return obj


def lathe(name, rings, mat, sides=12, center=(0,0,0), caps=True):
    verts = [(center[0]+r*math.cos(2*math.pi*i/sides),
              center[1]+r*math.sin(2*math.pi*i/sides), center[2]+z)
             for z,r in rings for i in range(sides)]
    faces = []
    for row in range(len(rings)-1):
        for i in range(sides):
            a=row*sides+i; b=row*sides+(i+1)%sides
            faces.append((a,b,b+sides,a+sides))
    if caps:
        faces += [tuple(reversed(range(sides))), tuple((len(rings)-1)*sides+i for i in range(sides))]
    return mesh(name, verts, faces, mat)


def beam(name, a, b, width, depth, mat='wood', bevel=.025):
    a,b = Vector(a),Vector(b)
    obj = cube(name,(0,0,0),(width,depth,(b-a).length),mat,bevel)
    transform=Matrix.Translation((a+b)/2) @ (b-a).to_track_quat('Z','Y').to_matrix().to_4x4()
    obj.data.transform(transform)
    return obj


def tube(name, points, radii, mat, sides=8, caps=True):
    points=[Vector(p) for p in points]
    if isinstance(radii,(int,float)): radii=[radii]*len(points)
    verts=[]
    for idx,p in enumerate(points):
        direction = points[min(idx+1,len(points)-1)]-points[max(idx-1,0)]
        rotation=direction.to_track_quat('Z','Y').to_matrix()
        for i in range(sides):
            angle=2*math.pi*i/sides
            verts.append(p+rotation @ Vector((radii[idx]*math.cos(angle),radii[idx]*math.sin(angle),0)))
    faces=[]
    for j in range(len(points)-1):
        for i in range(sides):
            a=j*sides+i; b=j*sides+(i+1)%sides
            faces.append((a,b,b+sides,a+sides))
    if caps: faces += [tuple(reversed(range(sides))),tuple((len(points)-1)*sides+i for i in range(sides))]
    return mesh(name,verts,faces,mat)


def torus(name, pos, major, minor, mat, axis='Z', sides=16, ring_sides=6):
    verts=[]
    rotation=Matrix.Identity(3)
    if axis=='Y': rotation=Matrix.Rotation(math.pi/2,3,'X')
    if axis=='X': rotation=Matrix.Rotation(math.pi/2,3,'Y')
    for i in range(sides):
        a=2*math.pi*i/sides
        for j in range(ring_sides):
            b=2*math.pi*j/ring_sides
            v=Vector(((major+minor*math.cos(b))*math.cos(a),
                       (major+minor*math.cos(b))*math.sin(a),minor*math.sin(b)))
            verts.append(Vector(pos)+rotation@v)
    faces=[(i*ring_sides+j,((i+1)%sides)*ring_sides+j,
            ((i+1)%sides)*ring_sides+(j+1)%ring_sides,i*ring_sides+(j+1)%ring_sides)
           for i in range(sides) for j in range(ring_sides)]
    return mesh(name,verts,faces,mat)


def empty(name, pos=(0,0,0)):
    obj=bpy.data.objects.new(name,None)
    CURRENT.objects.link(obj)
    obj.location=pos
    obj.empty_display_size=.06
    return obj


def attach_all(col, root):
    for obj in list(col.objects):
        if obj != root and obj.parent is None:
            obj.parent=root


def facet_colors(obj, names):
    for name in names:
        if M[name] not in list(obj.data.materials): obj.data.materials.append(M[name])
    for poly in obj.data.polygons:
        poly.material_index = RNG.randrange(len(obj.data.materials))


def shrub(pos, scale=.4):
    for i in range(4):
        p=(pos[0]+RNG.uniform(-.20,.20)*scale/.4,
           pos[1]+RNG.uniform(-.20,.20)*scale/.4,pos[2]+RNG.uniform(.10,.23)*scale/.4)
        obj=ico('Leaf cluster',p,(scale*.8,scale*.65,scale*.7),'leaf',2,.08)
        facet_colors(obj,['leaf','leaf_light','leaf_dark'])


def pine(pos, height=2.4):
    x,y,z=pos
    lathe('Pine trunk',[(0,.11),(.8*height,.065)],'bark',8,pos)
    for h,r in [(.12,.34),(.34,.29),(.56,.23)]:
        obj=lathe('Angular pine crown',[(h*height,r*height),((h+.13)*height,r*.70*height),
                                      ((h+.44)*height,.015)],'pine',7,pos)
        facet_colors(obj,['pine','pine_light'])


def lantern(pos, scale=1):
    x,y,z=pos
    cube('Lantern amber glass',(x,y,z),(.16*scale,.16*scale,.23*scale),'window',.015)
    for dx in [-.095,.095]:
        for dy in [-.095,.095]:
            cube('Lantern corner',(x+dx*scale,y+dy*scale,z),(.027*scale,.027*scale,.28*scale),'wood_dark',.004)
    lathe('Lantern roof',[(0,.155),(.09,.045)],'gold',4,(x,y,z+.15*scale))
    cube('Lantern bottom',(x,y,z-.14*scale),(.23*scale,.23*scale,.04*scale),'wood_dark',.008)
    torus('Lantern hanger',(x,y,z+.27*scale),.05*scale,.015*scale,'wood_dark','Y',12)


def barrel(pos, scale=1):
    x,y,z=pos
    lathe('Barrel staves',[(0,.25*scale),(.08*scale,.28*scale),(.30*scale,.31*scale),
                          (.52*scale,.28*scale),(.59*scale,.26*scale)],'wood_light',12,pos)
    for h in [.07,.49]: torus('Barrel iron hoop',(x,y,z+h*scale),.286*scale,.035*scale,'silver_dark')
    for i in range(12):
        a=i*math.tau/12
        beam('Stave seam',(x+.286*scale*math.cos(a),y+.286*scale*math.sin(a),z+.12*scale),
             (x+.288*scale*math.cos(a),y+.288*scale*math.sin(a),z+.46*scale),.008,.008,'wood_dark',0)
    lathe('Barrel lid',[(0,.254*scale),(.025*scale,.254*scale)],'wood_edge',12,(x,y,z+.59*scale))


def crate(pos, scale=.45):
    x,y,z=pos
    cube('Crate interior',(x,y,z+scale/2),(scale*.95,scale*.95,scale*.95),'wood_dark')
    for i in range(3):
        for sign in [-1,1]:
            cube('Crate plank',(x,y+sign*scale/2,z+(i+.5)*scale/3),(scale,.045,scale/3-.012),'wood_light',.008)
            cube('Crate plank',(x+sign*scale/2,y,z+(i+.5)*scale/3),(.045,scale,scale/3-.012),'wood_light',.008)
    for sign in [-1,1]:
        beam('Crate diagonal',(x-scale*.42,y+sign*(scale/2+.025),z+.07),
             (x+scale*.42,y+sign*(scale/2+.025),z+scale-.07),.06,.035,'wood_edge',.008)
    for i in [-1,0,1]: cube('Crate lid',(x+i*scale/3,y,z+scale),(scale/3-.01,scale,.04),'wood_light',.005)


def log(pos, length=.7, radius=.17, axis='Y'):
    direction=Vector((0,1,0) if axis=='Y' else (1,0,0) if axis=='X' else (0,0,1))
    a=Vector(pos); b=a+direction*length
    tube('Log bark',[a,b],radius,'bark',10)
    for p in [a-direction*.005,b+direction*.005]:
        tube('Cut log end',[p,p+direction*.007],radius*.91,'wood_edge',10)
        tube('Log growth ring',[p+direction*.009,p+direction*.011],radius*.60,'wood_light',10)
        tube('Log heart',[p+direction*.013,p+direction*.015],radius*.28,'wood_edge',10)


def flower(pos, scale=1):
    x,y,z=pos
    beam('Flower stem',(x,y,z),(x,y,z+.13*scale),.015,.015,'grass_dark',0)
    for i in range(5):
        a=i*math.tau/5
        ico('Flower petal',(x+.048*math.cos(a)*scale,y+.048*math.sin(a)*scale,z+.15*scale),
            (.045*scale,.035*scale,.024*scale),'flower',1)
    ico('Flower center',(x,y,z+.17*scale),(.025*scale,)*3,'gold',1)


def mushroom(pos, scale=.4, color='mushroom'):
    x,y,z=pos
    lathe('Mushroom stem',[(0,scale*.14),(scale*.50,scale*.10)],'cream',8,pos)
    lathe('Mushroom cap',[(scale*.40,scale*.50),(scale*.61,scale*.40),(scale*.84,.005)],color,10,pos)
    for angle in [-.8,-2,1.2]:
        ico('Mushroom spot',(x+math.cos(angle)*scale*.28,y+math.sin(angle)*scale*.28,z+scale*.66),
            (scale*.07,scale*.06,scale*.03),'cream',1)


def terrain(radius=2.55):
    lathe('Hex stone foundation',[(-.36,radius),(-.13,radius),(-.08,radius*.97)],'base',6)
    lathe('Hex earth rim',[(-.13,radius*.98),(-.045,radius*.98),(-.025,radius*.965)],'soil',6)
    lathe('Hex meadow',[(-.024,radius*.97),(.005,radius*.965)],'grass',6)
    # The meadow stays flat so each asset has a reliable ground-contact pivot.
    for _ in range(22):
        a=RNG.uniform(0,math.tau); r=RNG.uniform(radius*.72,radius*.86)
        x,y=math.cos(a)*r,math.sin(a)*r
        if RNG.random()<.28:
            rock=ico('Meadow stone',(x,y,.08),(RNG.uniform(.1,.2),.14,.11),'stone',1)
            facet_colors(rock,['stone','stone_light'])
        else:
            for j in range(4):
                a=j*math.tau/4+.35; h=RNG.uniform(.10,.18)
                transform=Matrix.Translation((x,y,0)) @ Matrix.Rotation(a,4,'Z')
                verts=[transform @ Vector(p) for p in [(0,0,.01),(-.045,.055,h*.48),
                        (0,.125,h),(.045,.055,h*.48),(0,.04,h*.6)]]
                mesh('Broad meadow leaf',verts,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],'grass_dark')
    meadow_scale=radius/2.55
    for x,y,z in [(-1.8,-.9,0),(1.7,.9,0),(-.5,1.9,0)]: shrub((x*meadow_scale,y*meadow_scale,z),.23)
    for x,y,z in [(-1.4,-1.4,0),(.9,-1.8,0)]: flower((x*meadow_scale,y*meadow_scale,z))


def stepping_stone(pos, size=.35):
    obj=ico('Path stepping stone',(pos[0],pos[1],.035),(size,size*.8,.06),'stone_light',1,.08)
    return obj


def chimney_smoke(pos=(.65,.50,4.03)):
    """Preview atmosphere; deliberately separate from the portable building mesh."""
    mat=bpy.data.materials.get('Chimney smoke volume') or bpy.data.materials.new('Chimney smoke volume')
    mat.use_nodes=True
    nodes=mat.node_tree.nodes; nodes.clear()
    volume=nodes.new('ShaderNodeVolumePrincipled')
    volume.inputs['Density'].default_value=.85
    volume.inputs['Color'].default_value=(.73,.71,.68,1)
    output=nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(volume.outputs['Volume'],output.inputs['Volume'])
    M['smoke_volume']=mat
    x,y,z=pos
    for i in range(6):
        radius=.08+i*.038
        ico('Soft chimney smoke',(x+.02*i,y+.017*i,z+.09+i*.13),(radius*.8,radius*.85,radius*1.2),'smoke_volume',2,.04)


def fence(a,b,posts=4,height=.65):
    a,b=Vector(a),Vector(b)
    for i in range(posts):
        p=a+(b-a)*i/(posts-1)
        cube('Fence post',p+Vector((0,0,height/2)),(.13,.13,height),'wood_light',.02)
    for z in [height*.37,height*.78]:
        beam('Fence rail',a+Vector((0,0,z)),b+Vector((0,0,z)),.11,.09,'wood_edge',.015)


def drop_reference_images(keep=None):
    """Discard packed references from previous assets in an owned worker file."""
    keep=Path(keep).resolve() if keep else None
    for image in list(bpy.data.images):
        if not image.filepath: continue
        path=Path(bpy.path.abspath(image.filepath)).resolve()
        if path.is_relative_to(ROOT/'sources/reference') and path!=keep:
            bpy.data.images.remove(image)


def clear_scene():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
    for obj in list(bpy.data.objects): bpy.data.objects.remove(obj,do_unlink=True)
    for col in list(bpy.data.collections): bpy.data.collections.remove(col)
    for action in list(bpy.data.actions): bpy.data.actions.remove(action)
    drop_reference_images()
    RNG.seed(407)
    palette()


def studio(target_z=1.6, scale=6.7):
    scene=bpy.context.scene
    col=collection('STUDIO — excluded from game exports'); target(col)
    cube('Studio ground',(0,0,-.415),(200,200,.10),'base',0)
    cam_data=bpy.data.cameras.new('Orthographic art camera')
    cam=bpy.data.objects.new('Orthographic art camera',cam_data); col.objects.link(cam)
    cam.location=(7,-11,8.0)
    cam.rotation_euler=(Vector((0,0,target_z))-cam.location).to_track_quat('-Z','Y').to_euler()
    enum(cam_data,'type','ORTHO'); cam_data.ortho_scale=scale; scene.camera=cam
    for name,loc,energy,size,color in [
        ('Warm key',(-3,-4,8),1100,5,(1,.86,.69)),
        ('Soft sky',(5,-1,5),650,5,(.72,.83,1)),
        ('Leaf rim',(1,5,7),1000,4,(1,.94,.73))]:
        data=bpy.data.lights.new(name,'AREA'); data.energy=energy; enum(data,'shape','DISK'); data.size=size; data.color=color
        light=bpy.data.objects.new(name,data); col.objects.link(light); light.location=loc
        light.rotation_euler=(Vector((0,0,1.3))-light.location).to_track_quat('-Z','Y').to_euler()
    scene.world=bpy.data.worlds.new('Neutral soft ambient')
    scene.world.use_nodes=True
    background=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
    background.inputs['Color'].default_value=(.20,.22,.25,1)
    background.inputs['Strength'].default_value=.45
    try: scene.render.engine='CYCLES'
    except TypeError: pass
    scene.cycles.samples=32; scene.cycles.use_denoising=True
    scene.render.resolution_x=900; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    enum(scene.render.image_settings,'file_format','PNG')
    # OCIO exposes a dynamic enum; preserve the valid transform from this installation.
    scene.render.film_transparent=False
    scene.render.fps=24
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                enum(area.spaces.active.region_3d,'view_perspective','CAMERA')
                enum(area.spaces.active.shading,'type','MATERIAL')
                area.spaces.active.overlay.show_overlays=False
    return col
