"""Static artifact tests, using existing-format GLBs without Blender."""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from .build_site import build_site
from .index import ROOT, write_json
from .test_catalog import glb


class StaticBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / 'dist/catalog'
        (self.root / 'catalog/vendor').mkdir(parents=True)
        for name in ('index.html', 'catalog.js', 'catalog.css'):
            (self.root / 'catalog' / name).write_bytes((ROOT / 'catalog' / name).read_bytes())
        (self.root / 'catalog/vendor/viewer.js').write_bytes(b'local viewer dependency')
        glb(self.root / 'exports/characters/hero.glb', clips=('rest', 'swing'))
        for name in ('sources/characters/hero.blend', 'sources/reference/sheet.png',
                     'exports/previews/hero.png', 'exports/thumbnails/characters/hero.png'):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(name.encode())
        write_json(self.root / 'catalog/associations.json', {'schema_version': 1, 'assets': {
            'exports/characters/hero.glb': {
                'preview': 'exports/previews/hero.png',
                'reference': {'path': 'sources/reference/sheet.png', 'crop': [0, 0, 20, 30]},
                'animation_policy': {'rest': True, 'swing': False}}}})

    def test_static_artifact_contains_only_viewer_and_referenced_models_images(self):
        before = (self.root / 'sources/characters/hero.blend').read_bytes()
        data = build_site(root=self.root)
        asset = data['assets'][0]
        self.assertIsNone(asset['source'])
        self.assertTrue(asset['source_excluded'])
        self.assertFalse(list(self.output.rglob('*.blend')))
        self.assertFalse((self.output / 'tools').exists())
        self.assertFalse((self.root / 'exports/catalog.json').exists())
        for key in ('model', 'reference', 'preview', 'thumbnail'):
            record = asset[key]
            copied = self.output / record['path']
            self.assertTrue(copied.is_file())
            self.assertEqual(record['version'], hashlib.sha256(copied.read_bytes()).hexdigest())
        self.assertEqual(asset['reference']['crop'], [0, 0, 20, 30])
        self.assertEqual([clip['loop'] for clip in asset['animations']], [True, False])
        self.assertEqual(before, (self.root / 'sources/characters/hero.blend').read_bytes())
        html = (self.output / 'index.html').read_text()
        self.assertIn('content="catalog.json"', html)
        self.assertIn('content="static"', html)
        self.assertNotIn('href="/', html)
        self.assertNotIn('src="/', html)
        self.assertTrue((self.output / 'catalog/vendor/viewer.js').exists())
        self.assertTrue((self.output / '.nojekyll').exists())

    def test_sources_are_explicitly_opt_in_and_removed_on_next_default_build(self):
        data = build_site(include_sources=True, root=self.root)
        self.assertTrue((self.output / data['assets'][0]['source']['path']).exists())
        self.assertNotIn('source_excluded', data['assets'][0])
        build_site(root=self.root)
        self.assertFalse(list(self.output.rglob('*.blend')))

    def test_file_timestamps_do_not_change_static_index_or_revision(self):
        first = build_site(root=self.root)
        contents = (self.output / 'catalog.json').read_bytes()
        for path in (self.root / 'sources/reference/sheet.png', self.root / 'exports/previews/hero.png'):
            os.utime(path, (1234567890, 1234567890))
        second = build_site(root=self.root)
        self.assertEqual(first['revision'], second['revision'])
        self.assertEqual(contents, (self.output / 'catalog.json').read_bytes())

    def test_rebuild_prunes_removed_exports_and_old_generated_files(self):
        glb(self.root / 'exports/props/extra.glb')
        build_site(root=self.root)
        self.assertTrue((self.output / 'exports/props/extra.glb').exists())
        (self.root / 'exports/props/extra.glb').unlink()
        (self.output / 'stale.txt').touch()
        build_site(root=self.root)
        self.assertFalse((self.output / 'exports/props/extra.glb').exists())
        self.assertFalse((self.output / 'stale.txt').exists())

    def test_builder_refuses_input_directories_and_unowned_output(self):
        for name in ('.', '..', 'sources', 'exports/site', 'catalog/generated', 'tools', 'dist'):
            if name == 'dist':
                (self.root / name).mkdir()
                (self.root / name / 'keep.txt').write_text('User file')
            with self.subTest(name=name), self.assertRaises(ValueError):
                build_site(name, root=self.root)
        self.assertEqual((self.root / 'dist/keep.txt').read_text(), 'User file')

    def test_bad_export_fails_build_and_keeps_last_artifact(self):
        build_site(root=self.root)
        previous = (self.output / 'catalog.json').read_bytes()
        (self.root / 'exports/characters/hero.glb').write_bytes(b'incomplete')
        with self.assertRaisesRegex(ValueError, 'Cannot build catalog'):
            build_site(root=self.root)
        self.assertEqual((self.output / 'catalog.json').read_bytes(), previous)

    def test_source_cannot_be_published_as_an_image(self):
        write_json(self.root / 'catalog/associations.json', {'schema_version': 1, 'assets': {
            'exports/characters/hero.glb': {'preview': 'sources/characters/hero.blend'}}})
        with self.assertRaisesRegex(ValueError, 'Unexpected file type for preview'):
            build_site(root=self.root)


if __name__ == '__main__':
    unittest.main()
