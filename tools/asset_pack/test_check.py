"""Incremental behavior, failures and dependency invalidation without Blender."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.asset_catalog.index import write_json
from tools.asset_pack.check import check_assets, digest


class IncrementalChecks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.ids=['props/alpha','props/beta']
        for asset in self.ids:
            source=self.root/'sources'/f'{asset}.blend'
            source.parent.mkdir(parents=True,exist_ok=True); source.write_bytes(b'authored source')
        write_json(self.root/'exports/asset_manifest.json', {'assets':[
            {'file':f'exports/{asset}.glb','source':f'sources/{asset}.blend'} for asset in self.ids]})
        worker=patch('tools.asset_pack.check.run_blender',side_effect=self.fake_worker)
        self.worker=worker.start()
        self.addCleanup(worker.stop)

    def fake_worker(self,script,args,**options):
        ids=list(args)[2:]
        if options['label']=='export':
            for asset in ids:
                path=self.root/'exports'/f'{asset}.glb'
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes((self.root/'sources'/f'{asset}.blend').read_bytes()+b' exported')
        else:
            path=self.root/'exports/validation.json'
            previous=json.loads(path.read_text()) if path.exists() else []
            records={a['asset_id']:a for a in previous}
            for asset in ids:
                records[asset]={'asset':asset,'asset_id':asset,'geometry_finite':True,
                    'source_sha256':digest(self.root/'sources'/f'{asset}.blend'),
                    'glb_sha256':digest(self.root/'exports'/f'{asset}.glb')}
            write_json(path,list(records.values()))
        return {'job':options['label'],'seconds':.01,'log':'fake.log'}

    def run_check(self,assets=None,**options):
        with contextlib.redirect_stdout(io.StringIO()):
            return check_assets(assets,root=self.root,blender='/fake/blender',**options)

    def test_warm_run_starts_no_workers_and_preserves_sources(self):
        before={a:digest(self.root/'sources'/f'{a}.blend') for a in self.ids}
        self.assertEqual(self.run_check()['verified'],2)
        self.worker.reset_mock()
        report=self.run_check()
        self.worker.assert_not_called()
        self.assertEqual(report['unchanged'],2)
        self.assertEqual(before,{a:digest(self.root/'sources'/f'{a}.blend') for a in self.ids})

    def test_source_edit_checks_only_changed_asset(self):
        self.run_check(); self.worker.reset_mock()
        (self.root/'sources/props/alpha.blend').write_bytes(b'edited source')
        self.assertEqual(self.run_check()['verified'],1)
        self.assertEqual(self.worker.call_count,2)
        for call in self.worker.call_args_list:
            self.assertEqual(call.args[1][2:],['props/alpha'])

    def test_corrupt_export_cannot_reuse_validation(self):
        self.run_check(); self.worker.reset_mock()
        (self.root/'exports/props/alpha.glb').write_bytes(b'corrupt export')
        self.assertEqual(self.run_check()['exported'],1)

    def test_verifier_change_revalidates_without_reexport(self):
        self.run_check(); self.worker.reset_mock()
        original=digest
        with patch('tools.asset_pack.check.digest',side_effect=lambda p:
                   'changed' if Path(p).name=='verify_pack.py' else original(p)):
            report=self.run_check()
        self.assertEqual(report['exported'],0)
        self.assertEqual(report['verified'],2)
        self.assertEqual(self.worker.call_count,1)

    def test_shared_library_change_invalidates_dependent_model_only(self):
        path=self.root/'sources/props/shared_village_kit.blend';path.write_bytes(b'kit one')
        manifest_path=self.root/'exports/asset_manifest.json'
        manifest=json.loads(manifest_path.read_text())
        manifest['shared_kit']='sources/props/shared_village_kit.blend'
        manifest['assets'][0]['shared_kit_instances']={'skull':2}
        write_json(manifest_path,manifest)
        self.run_check(self.ids); self.worker.reset_mock(); path.write_bytes(b'kit two')
        report=self.run_check(self.ids)
        self.assertEqual(report['verified'],1)
        self.assertEqual(self.worker.call_args.args[1][2:],['props/alpha'])
        self.worker.reset_mock()
        warm=self.run_check(self.ids)
        self.worker.assert_not_called()
        self.assertEqual(warm['embedded_kit_notices'],['props/alpha'])
        (self.root/'sources/props/alpha.blend').write_bytes(b'updated embedded kit')
        self.assertEqual(self.run_check(self.ids)['embedded_kit_notices'],[])

    def test_failure_never_records_successful_verification(self):
        self.worker.side_effect=RuntimeError('Blender failed')
        with self.assertRaises(RuntimeError):self.run_check()
        self.assertFalse((self.root/'.cache/asset-check/state.json').exists())
        report=json.loads((self.root/'.cache/asset-check/jobs.json').read_text())
        self.assertEqual(report['status'],'failed')

    def test_forest_dependency_uses_its_library_and_ignores_village_edits(self):
        forest=self.root/'sources/environment/shared_forest_kit.blend'
        forest.parent.mkdir(parents=True);forest.write_bytes(b'forest one')
        village=self.root/'sources/props/shared_village_kit.blend';village.write_bytes(b'village one')
        manifest_path=self.root/'exports/asset_manifest.json'
        manifest=json.loads(manifest_path.read_text())
        manifest['shared_kit']='sources/props/shared_village_kit.blend'
        manifest['assets'][0].update(shared_kit_instances={'forest_crystal_blue':2},
                                    shared_kits=['sources/environment/shared_forest_kit.blend'])
        write_json(manifest_path,manifest)
        self.run_check(self.ids);self.worker.reset_mock()
        village.write_bytes(b'village two')
        self.assertEqual(self.run_check(self.ids)['unchanged'],2)
        self.worker.assert_not_called()
        forest.write_bytes(b'forest two')
        report=self.run_check(self.ids)
        self.assertEqual(report['verified'],1)
        self.assertEqual(report['embedded_kit_notices'],['props/alpha'])

    def test_force_rechecks_unchanged_assets(self):
        self.run_check();self.worker.reset_mock()
        self.assertEqual(self.run_check(force=True)['verified'],2)

    def test_invalid_selection_fails_before_worker(self):
        with self.assertRaises(FileNotFoundError):self.run_check(['props/missing'])
        self.worker.assert_not_called()
