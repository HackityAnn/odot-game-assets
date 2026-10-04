"""Isolated GLB preview renderer. Never opens or saves a .blend source."""
import math
import sys

import bpy
from mathutils import Vector


def main():
    model, output = sys.argv[sys.argv.index('--') + 1:]
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=model)
    scene = bpy.context.scene
    scene.frame_set(1)
    bpy.context.view_layer.update()
    meshes = [obj for obj in scene.objects if obj.type == 'MESH']
    if not meshes:
        raise ValueError('Export has no renderable meshes')
    corners = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    low = Vector(tuple(min(corner[i] for corner in corners) for i in range(3)))
    high = Vector(tuple(max(corner[i] for corner in corners) for i in range(3)))
    center = (low + high) / 2
    radius = max((corner - center).length for corner in corners)
    radius = max(radius, .01)
    bpy.ops.object.camera_add(location=center + Vector((1, -1.5, .9)).normalized() * radius * 4)
    camera = bpy.context.object
    camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = radius * 2.35
    camera.data.clip_end = max(1000, radius * 10)
    scene.camera = camera
    # Constant illumination remains consistent across tiny props and buildings.
    for direction, energy in [((1, -2, 3), 2.4), ((-2, -1, 1), 1.2), ((0, 2, 2), 1.8)]:
        bpy.ops.object.light_add(type='SUN', location=center + Vector(direction) * radius * 3)
        light = bpy.context.object
        light.rotation_euler = (-Vector(direction)).to_track_quat('-Z', 'Y').to_euler()
        light.data.energy = energy
        light.data.angle = math.radians(15)
    scene.world = bpy.data.worlds.new('Catalog neutral background')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.08, .09, .07, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .5
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 24
    scene.render.resolution_x = scene.render.resolution_y = 480
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = output
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    main()
