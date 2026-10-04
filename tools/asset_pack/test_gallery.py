"""Build a gallery from a checkout fixture with no scratch folder or prior output."""
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from tools.asset_pack.gallery import build_gallery


class GalleryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.asset={'id':'knight','title':'Knight','category':'characters','batch':'original',
                    'reference':'fantasy_village.png','crop':[0,0,1,1],'dimensions':[1,1]}
        files=['sources/characters/knight.blend','exports/characters/knight.glb',
               'exports/previews/knight.png','sources/reference/fantasy_village.png',
               'sources/fantasy_village.blend','sources/autobattler.blend',
               'sources/evil_autobattler.blend','exports/previews/overview.png',
               'exports/previews/autobattler_overview.png','exports/previews/evil_overview.png',
               'sources/reference/autobattler/manifest.json',
               'sources/reference/evil_autobattler/manifest.json',
               'catalog/vendor/model-viewer.min.js','catalog/vendor/LICENSE-model-viewer',
               'catalog/vendor/draco/draco_decoder.wasm','README.md']
        for name in files:
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'fixture')
        (self.root/'exports/asset_manifest.json').write_text(json.dumps({'assets':[
            {'file':'exports/characters/knight.glb','triangles':12,'materials':1}]}))
        sha=lambda name:hashlib.sha256((self.root/name).read_bytes()).hexdigest()
        (self.root/'exports/validation.json').write_text(json.dumps([{'asset':'knight',
            'geometry_finite':True,'source_sha256':sha('sources/characters/knight.blend'),
            'glb_sha256':sha('exports/characters/knight.glb')}]))

    def test_clean_build_copies_viewer_license_dependencies_and_pack(self):
        with patch('tools.asset_pack.gallery.ASSETS',[self.asset]):path=build_gallery(self.root)
        self.assertFalse((self.root/'scratch').exists())
        self.assertTrue(path.is_file())
        for name in ['model-viewer.min.js','LICENSE-model-viewer','draco/draco_decoder.wasm']:
            self.assertEqual((path.parent/'vendor'/name).read_bytes(),(self.root/'catalog/vendor'/name).read_bytes())
        with zipfile.ZipFile(path.parent/'fantasy_village_assets.zip') as pack:
            self.assertIn('catalog/vendor/model-viewer.min.js',pack.namelist())
            self.assertIn('sources/characters/knight.blend',pack.namelist())

    def test_changed_source_marks_existing_validation_stale(self):
        (self.root/'sources/characters/knight.blend').write_bytes(b'manual edit')
        with patch('tools.asset_pack.gallery.ASSETS',[self.asset]):path=build_gallery(self.root)
        self.assertIn('validation=false;',path.read_text())
