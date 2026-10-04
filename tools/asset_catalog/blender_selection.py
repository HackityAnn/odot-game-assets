"""Select one authored asset, including its equipment, in a Blender worker."""
from pathlib import Path

import bpy


def load_asset(job, root):
    source = Path(root) / job['source']
    bpy.ops.wm.open_mainfile(filepath=str(source))
    name = Path(job['id']).name
    collection = None if job['object'] else bpy.data.collections.get(job['collection'] or name)
    asset_root = None if job['collection'] else bpy.data.objects.get(job['object'] or name)
    if collection is not None:
        if any(obj.name not in bpy.context.view_layer.objects for obj in collection.all_objects):
            bpy.context.scene.collection.children.link(collection)
            bpy.context.view_layer.update()
        objects = list(collection.all_objects)
    elif asset_root is not None:
        objects = [asset_root] + list(asset_root.children_recursive)
    else:
        raise ValueError(f'{source}: expected asset collection or root object named {name}')
    equipment = bpy.data.collections.get('EQUIPMENT')
    if equipment and collection and any(obj.type == 'ARMATURE' for obj in objects):
        objects = list(set(objects) | set(equipment.all_objects))
    if not objects:
        raise ValueError(f'{source}: empty asset collection')
    bpy.context.scene.frame_set(1)
    return sorted(objects, key=lambda obj: obj.name)
