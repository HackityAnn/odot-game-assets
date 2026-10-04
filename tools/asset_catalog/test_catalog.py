"""Focused discovery and merge tests using tiny GLB fixtures, no Blender."""
import json
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .index import CatalogIndex, write_json
from .metadata import read_glb


def glb(path, triangles=2, clips=()):
    document = {'asset': {'version': '2.0'}, 'materials': [{}, {}],
                'accessors': [{'count': triangles * 3}, {'count': 2, 'max': [1.5]}],
                'meshes': [{'primitives': [{'indices': 0}]}],
                'animations': [{'name': name, 'samplers': [{'input': 1}]} for name in clips]}
    chunk = json.dumps(document).encode()
    chunk += b' ' * (-len(chunk) % 4)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(struct.pack('<4sII', b'glTF', 2, len(chunk) + 20)
                     + struct.pack('<I4s', len(chunk), b'JSON') + chunk)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.index = CatalogIndex(self.root)

    def test_recursive_discovery_includes_unlisted_props_and_future_categories(self):
        for relative in ['buildings/house.glb', 'props/kit/tile.glb', 'future/fire.GLB', 'loose.glb']:
            glb(self.root / 'exports' / relative)
        data = self.index.build()
        self.assertEqual([asset['id'] for asset in data['assets']],
                         ['buildings/house', 'future/fire', 'loose', 'props/kit/tile'])
        self.assertEqual(data['assets'][2]['category'], 'uncategorized')
        self.assertTrue(all(asset['source'] is None for asset in data['assets']))

    def test_counts_and_clips_come_from_glb_and_merge_explicit_policy(self):
        key = 'exports/characters/hero.glb'
        glb(self.root / key, 7, ('rest', 'swing', 'unknown'))
        write_json(self.root / 'exports/asset_manifest.json', {
            'looping_clips': ['rest', 'swing'], 'one_shot_clips': [],
            'assets': [{'file': key, 'triangles': 999, 'animations': ['stale'],
                        'animation_policy': {'swing': False}}]})
        write_json(self.root / 'catalog/associations.json', {'schema_version': 1, 'assets': {
            key: {'title': 'Hero', 'animation_policy': {'rest': False}}}})
        asset = self.index.build()['assets'][0]
        self.assertEqual(asset['triangles'], 7)
        self.assertEqual(asset['materials'], 2)
        self.assertEqual([(clip['name'], clip['loop']) for clip in asset['animations']],
                         [('rest', False), ('swing', False), ('unknown', None)])
        self.assertEqual(asset['animations'][0]['duration'], 1.5)
        self.assertEqual(asset['title'], 'Hero')

    def test_pack_loop_defaults_do_not_leak_to_unlisted_exports(self):
        glb(self.root / 'exports/props/mover.glb', clips=('idle',))
        write_json(self.root / 'exports/asset_manifest.json', {'looping_clips': ['idle'], 'assets': []})
        self.assertIsNone(self.index.build()['assets'][0]['animations'][0]['loop'])

    def test_reference_requires_explicit_association_and_optional_files_refresh(self):
        key = 'exports/buildings/house.glb'
        glb(self.root / key)
        reference = self.root / 'sources/reference/house.png'
        reference.parent.mkdir(parents=True)
        reference.write_bytes(b'reference')
        self.assertIsNone(self.index.build()['assets'][0]['reference'])
        write_json(self.root / 'catalog/associations.json', {'schema_version': 1, 'assets': {
            key: {'reference': {'path': 'sources/reference/house.png', 'crop': [1, 2, 30, 40]}}}})
        data = self.index.build()
        self.assertEqual(data['assets'][0]['reference']['crop'], [1, 2, 30, 40])
        reference.unlink()
        changed = self.index.build()
        self.assertIsNone(changed['assets'][0]['reference'])
        self.assertNotEqual(changed['revision'], data['revision'])

    def test_live_change_reparses_only_changed_glb_and_index_is_stable(self):
        path = self.root / 'exports/props/sword.glb'
        glb(path, 1)
        first = self.index.refresh()
        stamp = (self.root / 'exports/catalog.json').stat().st_mtime_ns
        with patch('tools.asset_catalog.index.read_glb', wraps=read_glb) as reader:
            self.assertEqual(self.index.refresh(), first)
            self.assertEqual(reader.call_count, 0)
            self.assertEqual((self.root / 'exports/catalog.json').stat().st_mtime_ns, stamp)
            glb(path, 3)
            second = self.index.refresh()
            self.assertEqual(reader.call_count, 1)
        self.assertEqual(second['assets'][0]['triangles'], 3)
        self.assertNotEqual(first['assets'][0]['model']['version'], second['assets'][0]['model']['version'])
        path.unlink()
        self.assertEqual(self.index.refresh()['assets'], [])

    def test_corrupt_export_and_bad_json_do_not_hide_other_assets(self):
        path = self.root / 'exports/props/broken.glb'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'incomplete')
        glb(self.root / 'exports/props/valid.glb')
        (self.root / 'exports/asset_manifest.json').write_text('{')
        data = self.index.build()
        self.assertEqual(len(data['assets']), 2)
        self.assertIsNotNone(data['assets'][0]['error'])
        self.assertIsNone(data['assets'][1]['error'])
        self.assertEqual(len(data['warnings']), 1)

    def test_association_paths_cannot_escape_repository(self):
        glb(self.root / 'exports/props/item.glb')
        write_json(self.root / 'catalog/associations.json', {'schema_version': 1, 'assets': {
            'exports/props/item.glb': {'source': '/etc/passwd',
                                     'reference': {'path': '../../etc/passwd'}}}})
        asset = self.index.build()['assets'][0]
        self.assertIsNone(asset['source'])
        self.assertIsNone(asset['reference'])

    def test_invalid_metadata_shapes_still_allow_browsing(self):
        glb(self.root / 'exports/props/item.glb', clips=('turn',))
        write_json(self.root / 'exports/asset_manifest.json', {'assets': {}})
        write_json(self.root / 'catalog/associations.json', {'schema_version': 1, 'assets': {
            'exports/props/item.glb': {'title': {}, 'animation_policy': []}}})
        data = self.index.build()
        self.assertEqual(data['assets'][0]['title'], 'Item')
        self.assertIsNone(data['assets'][0]['animations'][0]['loop'])
        self.assertTrue(data['warnings'])


if __name__ == '__main__':
    unittest.main()
