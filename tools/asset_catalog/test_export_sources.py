"""Export planning is plain Python; these tests never launch Blender."""
import tempfile
import unittest
from pathlib import Path

from .export_sources import plan_exports
from .index import write_json


class ExportPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def source(self, path):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(b'BLENDER test source')

    def test_discovers_nested_new_sources_without_existing_glbs(self):
        self.source('sources/props/kit/lantern.blend')
        self.source('sources/future/cloud.blend')
        self.source('sources/overview.blend')
        jobs = plan_exports(self.root)
        self.assertEqual([job['id'] for job in jobs], ['future/cloud', 'props/kit/lantern'])

    def test_explicit_shared_sources_and_selection_work_without_existing_exports(self):
        self.source('sources/props/library.blend')
        self.source('sources/environment/tile.blend')
        write_json(self.root / 'exports/asset_manifest.json', {'assets': [
            {'file': 'exports/props/window.glb', 'source': 'sources/props/library.blend'}]})
        write_json(self.root / 'catalog/associations.json', {'schema_version': 1, 'assets': {
            'exports/props/window.glb': {'export_collection': 'Window components'},
            'exports/props/roof.glb': {'source': 'sources/props/library.blend', 'export_object': 'Roof'},
            'exports/environment/tile.glb': {'export_collection': 'DISPLAY_TERRAIN'}}})
        jobs = {job['id']: job for job in plan_exports(self.root)}
        self.assertEqual(set(jobs), {'props/window', 'props/roof', 'environment/tile'})
        self.assertEqual(jobs['props/window']['source'], 'sources/props/library.blend')
        self.assertEqual(jobs['props/window']['collection'], 'Window components')
        self.assertEqual(jobs['props/roof']['object'], 'Roof')

    def test_selection_rejects_missing_source_and_escape_paths(self):
        self.source('sources/props/sword.blend')
        self.assertEqual(plan_exports(self.root, ['props/sword'])[0]['id'], 'props/sword')
        with self.assertRaises(FileNotFoundError):
            plan_exports(self.root, ['props/missing'])
        with self.assertRaises(ValueError):
            plan_exports(self.root, ['../private'])
        write_json(self.root / 'catalog/associations.json', {'schema_version': 1, 'assets': {
            'exports/props/sword.glb': {'source': '/etc/passwd'}}})
        with self.assertRaises(FileNotFoundError):
            plan_exports(self.root, ['props/sword'])


if __name__ == '__main__':
    unittest.main()
