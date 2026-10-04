"""Resolve authored source exports and launch an isolated Blender worker."""
import subprocess
from pathlib import Path

from .index import CatalogIndex, ROOT


def plan_exports(root=ROOT, asset_ids=None):
    root = Path(root).resolve()
    index = CatalogIndex(root)
    warnings = []
    manifest = index.read_json('exports/asset_manifest.json', warnings)
    associations = index.read_json('catalog/associations.json', warnings)
    if associations and associations.get('schema_version') != 1:
        warnings.append('Unsupported catalog association schema_version')
    if not isinstance(manifest.get('assets', []), list):
        warnings.append('Export manifest assets must be an array')
    if not isinstance(associations.get('assets', {}), dict):
        warnings.append('Catalog association assets must be an object')
    if warnings:
        raise ValueError('\n'.join(warnings))
    metadata = {}
    for entry in manifest.get('assets', []):
        if isinstance(entry, dict) and isinstance(entry.get('file'), str):
            metadata[entry['file']] = entry
    for key, entry in associations.get('assets', {}).items():
        if isinstance(entry, dict):
            metadata[key] = metadata.get(key, {}) | entry
    candidates = {key.removeprefix('exports/').rsplit('.', 1)[0]
                  for key in metadata if key.startswith('exports/') and key.lower().endswith('.glb')}
    candidates.update(path.relative_to(root / 'exports').with_suffix('').as_posix()
                      for path in (root / 'exports').rglob('*') if path.suffix.lower() == '.glb')
    shared_sources = {entry['source'] for entry in metadata.values()
                      if isinstance(entry.get('source'), str)}
    # Root-level .blend files are overview scenes. Shared libraries are only
    # exported through explicit per-asset mappings, never as one giant model.
    for path in (root / 'sources').rglob('*.blend'):
        relative = path.relative_to(root / 'sources')
        if len(relative.parts) > 1 and path.relative_to(root).as_posix() not in shared_sources:
            candidates.add(relative.with_suffix('').as_posix())
    jobs = []
    for asset_id in sorted(set(asset_ids) if asset_ids is not None else candidates):
        relative = Path(asset_id)
        if relative.is_absolute() or '..' in relative.parts or relative.suffix:
            raise ValueError(f'Invalid asset ID: {asset_id}')
        entry = metadata.get('exports/' + asset_id + '.glb', {})
        if entry.get('export_collection') and entry.get('export_object'):
            raise ValueError(f'{asset_id}: choose export_collection or export_object, not both')
        source_name = entry.get('source', 'sources/' + asset_id + '.blend')
        source = index.local_file(source_name)
        if not source:
            if asset_ids is not None:
                raise FileNotFoundError(f'{asset_id}: missing editable source {source_name}')
            continue
        if Path(source['path']).suffix != '.blend':
            raise ValueError(f'{asset_id}: source must be a .blend file')
        jobs.append({'id': asset_id, 'source': source['path'],
                     'collection': entry.get('export_collection'),
                     'object': entry.get('export_object')})
    if not jobs:
        raise ValueError('No editable asset sources found')
    return jobs


def export_sources(asset_ids, blender='blender', root=ROOT):
    plan_exports(root, asset_ids)  # Validate before launching Blender.
    args = asset_ids if asset_ids else ['--all']
    subprocess.run([blender, '-b', '--factory-startup', '--python-exit-code', '1',
                    '--python', str(Path(__file__).with_name('export_blender.py')),
                    '--', '--root', str(Path(root).resolve()), *args], check=True)
