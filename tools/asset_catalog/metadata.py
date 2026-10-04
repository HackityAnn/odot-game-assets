"""Read export facts without Blender or any changes to the assets."""
import hashlib
import json
import struct
from pathlib import Path


def read_glb(path: Path) -> dict:
    """Inspect the JSON chunk only; hashing provides a cache-safe model URL."""
    with path.open('rb') as stream:
        magic, version, length = struct.unpack('<4sII', stream.read(12))
        if magic != b'glTF' or version != 2 or length != path.stat().st_size:
            raise ValueError('Not a complete glTF 2 binary')
        size, kind = struct.unpack('<I4s', stream.read(8))
        if kind != b'JSON' or size > length - 20:
            raise ValueError('Missing or incomplete GLB JSON chunk')
        document = json.loads(stream.read(size))
        if not isinstance(document, dict):
            raise ValueError('GLB JSON must be an object')
        stream.seek(0)
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    accessors = document.get('accessors', [])
    triangles = 0
    for mesh in document.get('meshes', []):
        for primitive in mesh.get('primitives', []):
            accessor = primitive.get('indices', primitive.get('attributes', {}).get('POSITION'))
            count = accessors[accessor]['count'] if accessor is not None else 0
            mode = primitive.get('mode', 4)
            if mode == 4:
                triangles += count // 3
            elif mode in (5, 6):
                triangles += max(0, count - 2)
    clips = []
    for number, animation in enumerate(document.get('animations', [])):
        ends = [accessors[s['input']].get('max', [None])[0]
                for s in animation.get('samplers', [])]
        ends = [end for end in ends if isinstance(end, (int, float))]
        extras = animation.get('extras')
        loop = extras.get('loop') if isinstance(extras, dict) else None
        clips.append({'name': animation.get('name') or f'animation_{number}',
                      'duration': max(ends) if ends else None,
                      'loop': loop if isinstance(loop, bool) else None})
    return {'bytes': length, 'triangles': triangles,
            'materials': len(document.get('materials', [])), 'animations': clips,
            'version': digest}


def merge_metadata(facts: dict, manifest: dict, asset: dict, association: dict) -> dict:
    """GLB counts win. Explicit asset clip policy wins over pack-wide defaults."""
    result = dict(facts)
    result['title'] = association.get('title', asset.get('title'))
    asset_policy = asset.get('animation_policy', {})
    association_policy = association.get('animation_policy', {})
    policy = (asset_policy if isinstance(asset_policy, dict) else {}) | (
        association_policy if isinstance(association_policy, dict) else {})
    result['animations'] = []
    for clip in facts.get('animations', []):
        clip = dict(clip)
        name = clip['name']
        if name in policy and isinstance(policy[name], bool):
            clip['loop'] = policy[name]
        elif clip.get('loop') is None:
            one_shots = manifest.get('one_shot_clips')
            looping = manifest.get('looping_clips')
            if isinstance(one_shots, list) and name in one_shots:
                clip['loop'] = False
            elif isinstance(looping, list) and name in looping:
                clip['loop'] = True
        result['animations'].append(clip)
    return result
