"""Read-only mechanical art checks. Visual similarity remains a review decision."""
import math

import art_style as style


def _principled(mat):
    if mat is None or not mat.use_nodes:
        return None
    output = next((node for node in mat.node_tree.nodes
                   if node.type == 'OUTPUT_MATERIAL' and node.is_active_output), None)
    if output is None or not output.inputs['Surface'].links:
        return None
    shader = output.inputs['Surface'].links[0].from_node
    return shader if shader.type == 'BSDF_PRINCIPLED' else None


def _texture(socket):
    if not socket.links:
        return None
    node = socket.links[0].from_node
    if node.type == 'NORMAL_MAP':
        return _texture(node.inputs['Color'])
    return node.image if node.type == 'TEX_IMAGE' else None


def material_violations(mat, painted=False):
    errors = []
    shader = _principled(mat)
    if shader is None:
        return [mat.name + ': use a Principled BSDF material']
    for field in ('Roughness', 'Metallic'):
        value = shader.inputs[field].default_value
        if not math.isfinite(value) or not 0 <= value <= 1:
            errors.append(mat.name + ': invalid ' + field)
    family = mat.get('texture_family') or style.material_family(mat.name)
    if not (painted or mat.get('painted_finish')) or family is None:
        return errors
    required = ['Base Color', 'Roughness']
    if family in style.NORMAL_FAMILIES:
        required.append('Normal')
    if shader.inputs['Emission Strength'].default_value > 0:
        required.append('Emission Color')
    for field in required:
        image = _texture(shader.inputs[field])
        if image is None:
            errors.append(mat.name + ': missing baked ' + field + ' image')
            continue
        receiving = mat.get('receiving_ground') or mat.name.startswith('Painted receiving ground ')
        expected_size = (style.TEXTURES.ground_size if receiving and field in ('Base Color','Emission Color')
                         else style.TEXTURES.size_for(family))
        if min(image.size) < expected_size:
            errors.append(mat.name + ': ' + field + ' image is below ' + str(expected_size) + ' px')
        if not image.packed_file:
            errors.append(mat.name + ': pack the ' + field + ' image')
        expected_space = style.TEXTURES.data_space if field in ('Normal', 'Roughness') else style.TEXTURES.color_space
        if image.colorspace_settings.name != expected_space:
            errors.append(mat.name + ': ' + field + ' needs ' + expected_space + ' color space')
        if field == 'Normal':
            node = shader.inputs[field].links[0].from_node
            if node.type != 'NORMAL_MAP' or node.space != 'TANGENT':
                errors.append(mat.name + ': use a tangent-space Normal Map node')
    return errors


def asset_violations(objects, category, *, painted=False, scene=None):
    errors = []
    materials = {slot.material for obj in objects if obj.type == 'MESH'
                 for slot in obj.material_slots if slot.material}
    for mat in sorted(materials, key=lambda mat: mat.name):
        errors.extend(material_violations(mat, painted))
    for obj in objects:
        if obj.type != 'MESH':
            continue
        shaders = [_principled(slot.material) for slot in obj.material_slots]
        if any(shader and _texture(shader.inputs['Base Color']) for shader in shaders):
            if not obj.data.uv_layers:
                errors.append(obj.name + ': textured mesh needs UVs')
            elif not all(math.isfinite(c) for loop in obj.data.uv_layers.active.data for c in loop.uv):
                errors.append(obj.name + ': nonfinite UVs')
        if obj.name.startswith('Faceted magical crystal') and any(p.use_smooth for p in obj.data.polygons):
            errors.append(obj.name + ': keep crystal facet normals flat')
        if obj.name.startswith(('Broad faceted mushroom cap', 'Curving luminous mushroom stem', 'Broad woodland leaf')):
            if not any(p.use_smooth for p in obj.data.polygons):
                errors.append(obj.name + ': smooth the organic surface normals')
        if obj.name.startswith(('Mushroom cyan ground bounce', 'Crystal ground reflection',
                                'Lantern warm ground bounce', 'Rock root contact shade')):
            errors.append(obj.name + ': paint feathered shading onto the receiving surface')
    roots = [obj for obj in objects if obj.name.endswith('_root') and obj.parent is None]
    for root in roots:
        if root.location.length > style.GEOMETRY.pivot_tolerance:
            errors.append(root.name + ': ground pivot must remain at the origin')
        if 'hex_radius' in root:
            for field, value in [('hex_radius', style.HEX.radius), ('grid_spacing_x', style.HEX.spacing_x),
                                 ('grid_spacing_y', style.HEX.spacing_y)]:
                if abs(root.get(field, math.inf) - value) > style.GEOMETRY.pivot_tolerance:
                    errors.append(root.name + ': incorrect ' + field)
            points = [obj.matrix_world @ vertex.co for obj in objects if obj.type == 'MESH' for vertex in obj.data.vertices]
            if points and abs(min(p.z for p in points) - style.HEX.bottom) > style.GEOMETRY.pivot_tolerance:
                errors.append(root.name + ': incorrect hex foundation height')
            if any(not style.HEX.contains(p.x, p.y, style.GEOMETRY.footprint_tolerance) for p in points):
                errors.append(root.name + ': geometry crosses the shared hex footprint')
    if category == 'characters':
        if scene is not None and scene.render.fps != style.UNITS.fps:
            errors.append('Unit animation FPS differs from the shared preset')
        rigs = [obj for obj in objects if obj.type == 'ARMATURE']
        if len(rigs) != 1:
            errors.append('Unit needs one armature')
        else:
            rig = rigs[0]
            if len(rig.data.bones) != style.UNITS.bone_count:
                errors.append(rig.name + ': incorrect shared bone count')
            for socket in style.UNITS.sockets:
                bone = rig.data.bones.get(socket)
                used = any(obj.parent_type == 'BONE' and obj.parent_bone == socket for obj in objects)
                if bone is None or (used and bone.use_deform):
                    errors.append(rig.name + ': missing or deforming ' + socket)
            clips = {strip.action.name for track in rig.animation_data.nla_tracks for strip in track.strips
                     if strip.action} if rig.animation_data else set()
            if clips != set(style.CLIP_FRAMES):
                errors.append(rig.name + ': unit needs the shared six animation clips')
    return errors


def preview_violations(scene):
    spec = style.PREVIEW
    errors = []
    if (scene.render.resolution_x, scene.render.resolution_y) != (spec.resolution, spec.resolution):
        errors.append('Preview resolution differs from the shared preset')
    if scene.render.engine != spec.engine or scene.cycles.samples != spec.samples:
        errors.append('Preview engine/samples differ from the shared preset')
    if scene.view_settings.view_transform != spec.transform or scene.view_settings.look != spec.look:
        errors.append('Preview color management differs from the shared preset')
    if scene.render.fps != style.UNITS.fps:
        errors.append('Preview animation FPS differs from the shared preset')
    for light in style.LIGHTS:
        obj = next((obj for obj in scene.objects if obj.type == 'LIGHT' and style.material_name(obj.name) == light.name), None)
        if obj is None or obj.data.type != 'AREA':
            errors.append(light.name + ': preview needs the shared Area Light')
        elif abs(obj.data.energy - light.energy) > .01 or abs(obj.data.size - light.size) > .0001:
            errors.append(light.name + ': energy/size differs from the shared preset')
    return errors
