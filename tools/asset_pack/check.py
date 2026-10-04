"""Incrementally export and verify selected authored assets; never rebuild sources."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from tools.asset_catalog.export_sources import plan_exports
from tools.asset_catalog.index import ROOT, write_json
from tools.asset_pack.catalog import BY_ID
from tools.asset_pack.worker import resolve_blender, run_blender

EXPORT_CODE = ('tools/asset_catalog/export_blender.py',
               'tools/asset_catalog/blender_selection.py',
               'tools/asset_catalog/export_sources.py', 'tools/asset_catalog/index.py',
               'tools/asset_catalog/metadata.py')
VERIFY_CODE = ('tools/asset_pack/verify_pack.py', 'tools/asset_pack/export_pack.py',
               'tools/asset_pack/geometry.py', 'tools/asset_pack/catalog.py',
               'tools/asset_catalog/blender_selection.py')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def canonical(asset):
    if asset in BY_ID:
        return BY_ID[asset]['category'] + '/' + asset
    return asset


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def check_assets(assets=None, *, root=ROOT, blender=None, force=False):
    root=Path(root).resolve()
    jobs=plan_exports(root, [canonical(asset) for asset in assets] if assets else None)
    executable=resolve_blender(blender)
    binary=Path(executable)
    runtime={'path':executable}
    if binary.is_file():
        runtime['size']=binary.stat().st_size
        runtime['modified']=binary.stat().st_mtime_ns
    manifest=read(root/'exports/asset_manifest.json', {})
    entries={a['file']:a for a in manifest.get('assets', [])}
    state_path=root/'.cache/asset-check/state.json'
    state=read(state_path, {'schema_version':1,'assets':{}})
    if state.get('schema_version')!=1:
        state={'schema_version':1,'assets':{}}
    validation=read(root/'exports/validation.json', [])
    checked={a.get('asset_id',canonical(a['asset'])):a for a in validation}
    export_code={path:digest(ROOT/path) for path in EXPORT_CODE}
    verify_code={path:digest(ROOT/path) for path in VERIFY_CODE}
    pending={}; export_ids=[]; verify_ids=[]; notices=[]
    for job in jobs:
        asset_id=job['id']; target=root/'exports'/f'{asset_id}.glb'
        inputs={'job':job,'source':digest(root/job['source']),'runtime':runtime}
        entry=entries.get(f'exports/{asset_id}.glb',{})
        if entry.get('shared_kit_instances'):
            libraries=entry.get('shared_kits') or [manifest.get('shared_kit','sources/props/shared_village_kit.blend')]
            hashes={}
            for library in libraries:
                path=(root/library).resolve()
                if not path.is_relative_to(root) or not path.is_file():
                    raise ValueError(f'{asset_id}: missing or invalid shared kit {library}')
                hashes[library]=digest(path)
            inputs['shared_kit']=hashes
        before=state['assets'].get(asset_id,{})
        previous_kit=before.get('shared_kit')
        if isinstance(previous_kit,str):
            previous_kit={manifest.get('shared_kit','sources/props/shared_village_kit.blend'):previous_kit}
        needs_rebuild=(before.get('source_sha256')==inputs['source'] and
                       (before.get('needs_kit_rebuild') or
                        (previous_kit and previous_kit!=inputs.get('shared_kit'))))
        if needs_rebuild:
            notices.append(asset_id)
            print(f'{asset_id}: shared kit changed; embedded copies need a modeling rebuild. '
                  'This check exports the existing source.',flush=True)
        export_input=fingerprint({'inputs':inputs,'code':export_code})
        verify_input=fingerprint({'inputs':inputs,'code':verify_code})
        model_hash=digest(target) if target.is_file() else None
        needs_export=(force or before.get('export_input')!=export_input
                      or before.get('glb_sha256')!=model_hash or model_hash is None)
        record=checked.get(asset_id,{})
        current=(record.get('geometry_finite') is True
                 and record.get('source_sha256')==inputs['source']
                 and record.get('glb_sha256')==model_hash)
        needs_verify=(needs_export or force or before.get('verify_input')!=verify_input or not current)
        if needs_export: export_ids.append(asset_id)
        if needs_verify: verify_ids.append(asset_id)
        else: print(f'Unchanged and verified: {asset_id}',flush=True)
        pending[asset_id]={'export_input':export_input,'verify_input':verify_input,
                           'source_sha256':inputs['source'],'shared_kit':inputs.get('shared_kit'),
                           'needs_kit_rebuild':bool(needs_rebuild)}
    report={'status':'running','selected':len(jobs),'exported':len(export_ids),'verified':len(verify_ids),
            'unchanged':len(jobs)-len(verify_ids),'embedded_kit_notices':notices,'jobs':[]}
    report_path=root/'.cache/asset-check/jobs.json'
    write_json(report_path,report)
    if export_ids:
        try:
            report['jobs'].append(run_blender('tools/asset_catalog/export_blender.py',
                ['--root',root,*export_ids],blender=executable,root=root,label='export'))
        except Exception as error:
            write_json(report_path,report | {'status':'failed','error':str(error)})
            raise
    if verify_ids:
        try:
            report['jobs'].append(run_blender('tools/asset_pack/verify_pack.py',
                ['--root',root,*verify_ids],blender=executable,root=root,label='verify'))
        except Exception as error:
            write_json(report_path,report | {'status':'failed','error':str(error)})
            raise
        checked={a.get('asset_id',canonical(a['asset'])):a
                 for a in read(root/'exports/validation.json',[])}
        for job in jobs:
            asset_id=job['id']
            if asset_id not in verify_ids: continue
            source_hash=digest(root/job['source'])
            model_hash=digest(root/'exports'/f'{asset_id}.glb')
            record=checked.get(asset_id,{})
            if (record.get('geometry_finite') is not True
                    or source_hash!=pending[asset_id]['source_sha256']
                    or record.get('source_sha256')!=source_hash
                    or record.get('glb_sha256')!=model_hash):
                error=f'{asset_id}: validation failed or files changed during the check'
                write_json(report_path,report | {'status':'failed','error':error})
                raise RuntimeError(error)
            state['assets'][asset_id]=pending[asset_id] | {'glb_sha256':model_hash}
        write_json(state_path,state)
    report['status']='passed'
    write_json(report_path,report)
    print(f"Asset check: {report['exported']} exported, {report['verified']} verified, "
          f"{report['unchanged']} unchanged",flush=True)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('assets',nargs='*',help='Short model names or canonical IDs, e.g. props/kit_skull')
    parser.add_argument('--all',action='store_true',help='Check all models, props and terrain')
    parser.add_argument('--force',action='store_true',help='Ignore cached results')
    parser.add_argument('--blender',help='Executable; defaults to BLENDER, PATH, then the local pinned install')
    args=parser.parse_args()
    if not args.assets and not args.all:
        parser.error('Supply asset IDs or --all')
    check_assets(args.assets or None,blender=args.blender,force=args.force)


if __name__=='__main__':
    try:
        main()
    except (OSError,ValueError,RuntimeError) as error:
        print(str(error),file=sys.stderr)
        sys.exit(1)
