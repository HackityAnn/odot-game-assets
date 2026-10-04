"""Apply shared settings to Blender datablocks; builders own scene creation."""
import bpy

import art_style as style


def stone_edges(obj):
    if not any(mod.type == 'BEVEL' for mod in obj.modifiers):
        mod = obj.modifiers.new('Subtle worn stone bevel', 'BEVEL')
        mod.width = style.GEOMETRY.stone_bevel_width
        mod.segments = style.GEOMETRY.bevel_segments
        mod.limit_method = 'ANGLE'
        mod.angle_limit = style.GEOMETRY.stone_bevel_angle
        mod.harden_normals = True
    if not any(mod.type == 'WEIGHTED_NORMAL' for mod in obj.modifiers):
        normal = obj.modifiers.new('Preserve broad stone facet normals', 'WEIGHTED_NORMAL')
        normal.keep_sharp = True


def smooth_sides(obj):
    for polygon in obj.data.polygons:
        polygon.use_smooth = len(polygon.vertices) == 4


def preview(scene):
    """Idempotent setup: repeat calls never multiply light energy or add halos."""
    spec = style.PREVIEW
    scene.render.engine = spec.engine
    scene.render.resolution_x = scene.render.resolution_y = spec.resolution
    scene.render.resolution_percentage = 100
    scene.cycles.samples = spec.samples
    scene.cycles.use_denoising = True
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = spec.threads
    scene.render.fps = style.UNITS.fps
    scene.view_settings.view_transform = spec.transform
    scene.view_settings.look = spec.look
    if scene.world is None:
        scene.world = bpy.data.worlds.new('Neutral soft ambient')
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get('Background')
    background.inputs['Color'].default_value = (*spec.world_color, 1)
    background.inputs['Strength'].default_value = spec.world_strength
    lights = {light.name: light for light in style.LIGHTS}
    for obj in scene.objects:
        light = lights.get(style.material_name(obj.name))
        if obj.type == 'LIGHT' and light:
            obj.data.energy = light.energy
            obj.data.size = light.size
            obj.data.color = light.color
    tree = scene.compositing_node_group
    if tree is None:
        tree = bpy.data.node_groups.new('Soft magical highlights', 'CompositorNodeTree')
        tree.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        render = tree.nodes.new('CompositorNodeRLayers')
        glare = tree.nodes.new('CompositorNodeGlare')
        output = tree.nodes.new('NodeGroupOutput')
        tree.links.new(render.outputs['Image'], glare.inputs['Image'])
        tree.links.new(glare.outputs['Image'], output.inputs['Image'])
        scene.compositing_node_group = tree
    glare = next((node for node in tree.nodes if node.type == 'GLARE'), None)
    if glare is None:
        raise ValueError('The authored preview compositor needs a Glare node')
    glare.inputs['Type'].default_value = 'Fog Glow'
    glare.inputs['Quality'].default_value = 'High'
    glare.inputs['Threshold'].default_value = spec.glare_threshold
    glare.inputs['Strength'].default_value = spec.glare_strength
    glare.inputs['Size'].default_value = spec.glare_size
    scene['game_art_style'] = style.STYLE_ID
