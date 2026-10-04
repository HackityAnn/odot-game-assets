"""Read-only audit of UVs, packed maps and texture channels in finished GLBs."""
import json
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.asset_catalog.blender_selection import load_asset
from tools.asset_catalog.export_sources import plan_exports


def source_channels(mat):
    shader = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    channels = {}
    if shader is None:
        return channels
    for socket, field in [('Base Color', 'baseColorTexture'), ('Roughness', 'metallicRoughnessTexture'),
                          ('Normal', 'normalTexture'), ('Emission Color', 'emissiveTexture')]:
        links = shader.inputs[socket].links
        if not links:
            continue
        node = links[0].from_node
        if node.type == 'NORMAL_MAP':
            node = node.inputs['Color'].links[0].from_node
        assert node.type == 'TEX_IMAGE', (mat.name, socket, 'map was not baked')
        image = node.image
        assert image and image.packed_file, (mat.name, socket, 'missing packed image')
        assert min(image.size) >= 512, (mat.name, socket, 'low resolution map')
        channels[field] = image.name
    return channels


def main(ids):
    reports = []
    for job in plan_exports(ROOT, ids):
        objects = load_asset(job, ROOT)
        materials = {slot.material for obj in objects if obj.type == 'MESH'
                     for slot in obj.material_slots if slot.material}
        expected = {mat.name: source_channels(mat) for mat in materials
                    if mat.get('painted_finish')}
        for obj in objects:
            if obj.type != 'MESH':
                continue
            if any(slot.material and slot.material.name in expected for slot in obj.material_slots):
                assert obj.data.uv_layers, (job['id'], obj.name, 'missing UVs')
                assert all(math.isfinite(c) for loop in obj.data.uv_layers.active.data
                           for c in loop.uv), (job['id'], obj.name, 'invalid UVs')
        data = (ROOT / 'exports' / (job['id'] + '.glb')).read_bytes()
        length, kind = struct.unpack_from('<II', data, 12)
        assert kind == 0x4E4F534A, job['id']
        document = json.loads(data[20:20 + length])
        exported = {mat['name']: mat for mat in document.get('materials', [])}
        for name, channels in expected.items():
            assert name in exported, (job['id'], name, 'material missing')
            mat = exported[name]
            for channel in channels:
                owner = mat.get('pbrMetallicRoughness', {}) if channel in (
                    'baseColorTexture', 'metallicRoughnessTexture') else mat
                assert channel in owner, (job['id'], name, channel, 'map lost in export')
                texture = document['textures'][owner[channel]['index']]
                image = document['images'][texture['source']]
                assert 'bufferView' in image and image.get('mimeType') == 'image/png', (
                    job['id'], name, channel, 'image not embedded')
        for mesh in document.get('meshes', []):
            for primitive in mesh['primitives']:
                mat = document['materials'][primitive['material']]
                if mat['name'] in expected and expected[mat['name']]:
                    assert 'TEXCOORD_0' in primitive['attributes'], (job['id'], 'UVs lost in export')
                    assert 'NORMAL' in primitive['attributes'], (job['id'], 'normals lost in export')
        reports.append({'asset_id': job['id'], 'textured_materials': len(expected),
                        'embedded_images': len(document.get('images', [])),
                        'uvs_and_material_channels_verified': True})
        print('Verified portable painted finish:', job['id'], flush=True)
    path = ROOT / '.cache/softness/texture-validation.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(reports, indent=2) + '\n')
    print('Verified painted UVs, packed images and exported channels:', len(reports))


if __name__ == '__main__':
    main(sys.argv[sys.argv.index('--') + 1:])
