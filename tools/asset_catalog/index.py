"""Recursive discovery, explicit associations, and a disposable catalog index."""
import hashlib
import json
import os
import struct
import tempfile
from pathlib import Path

from .metadata import merge_metadata, read_glb

ROOT = Path(__file__).resolve().parents[2]


def write_json(path: Path, data: dict):
    """Replace atomically, and leave unchanged output alone."""
    content = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
    if path.exists() and path.read_text() == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(content)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


class CatalogIndex:
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve()
        self.cache = {}

    def local_file(self, name):
        if not isinstance(name, str):
            return None
        path = (self.root / name).resolve()
        if not path.is_relative_to(self.root) or not path.is_file():
            return None
        stat = path.stat()
        version = f'{stat.st_mtime_ns:x}-{stat.st_ctime_ns:x}-{stat.st_size:x}'
        return {'path': path.relative_to(self.root).as_posix(), 'version': version}

    def read_json(self, name, warnings):
        path = self.root / name
        if not path.exists():
            return {}
        try:
            value = json.loads(path.read_text())
            if not isinstance(value, dict):
                raise ValueError('expected an object')
            return value
        except (OSError, ValueError) as error:
            warnings.append(f'{name}: {error}')
            return {}

    def build(self):
        warnings = []
        manifest = self.read_json('exports/asset_manifest.json', warnings)
        associations = self.read_json('catalog/associations.json', warnings)
        if associations and associations.get('schema_version') != 1:
            warnings.append('catalog/associations.json: unsupported schema_version')
            associations = {}
        manifest_assets = manifest.get('assets', [])
        if not isinstance(manifest_assets, list):
            warnings.append('exports/asset_manifest.json: assets must be an array')
            manifest_assets = []
        entries = {entry.get('file'): entry for entry in manifest_assets
                   if isinstance(entry, dict) and isinstance(entry.get('file'), str)}
        mappings = associations.get('assets', {})
        if not isinstance(mappings, dict):
            warnings.append('catalog/associations.json: assets must be an object')
            mappings = {}
        assets = []
        seen = set()
        for path in sorted((self.root / 'exports').rglob('*')):
            if not path.is_file() or path.suffix.lower() != '.glb':
                continue
            if not path.resolve().is_relative_to(self.root):
                continue
            key = path.relative_to(self.root).as_posix()
            seen.add(key)
            try:
                stat = path.stat()
                stamp = (stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size, stat.st_ino)
                cached = self.cache.get(key)
                if cached and cached[0] == stamp:
                    facts = cached[1]
                else:
                    facts = read_glb(path)
                    self.cache[key] = (stamp, facts)
                error = None
            except (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError, struct.error) as failure:
                facts = {'bytes': path.stat().st_size if path.exists() else None,
                         'triangles': None, 'materials': None, 'animations': [],
                         'version': self.local_file(key)['version'] if path.exists() else ''}
                error = f'Cannot inspect export: {failure}'
            entry = entries.get(key, {})
            association = mappings.get(key, {})
            if not isinstance(association, dict):
                warnings.append(f'{key}: association must be an object')
                association = {}
            metadata = merge_metadata(facts, manifest if entry else {}, entry, association)
            if not isinstance(metadata.get('title'), str):
                metadata['title'] = None
            relative = path.relative_to(self.root / 'exports')
            asset_id = relative.with_suffix('').as_posix()
            category = relative.parts[0] if len(relative.parts) > 1 else 'uncategorized'
            source = association.get('source', entry.get('source',
                         'sources/' + relative.with_suffix('.blend').as_posix()))
            # Legacy previews are only associated by matching manifest entries.
            preview = association.get('preview', entry.get('preview'))
            if preview is None and entry:
                preview = f'exports/previews/{path.stem}.png'
            thumbnail = association.get('thumbnail',
                                        f'exports/thumbnails/{asset_id}.png')
            reference = association.get('reference', entry.get('reference'))
            if isinstance(reference, str):
                reference = {'path': reference}
            ref = self.local_file(reference.get('path')) if isinstance(reference, dict) else None
            if ref and reference.get('crop'):
                crop = reference['crop']
                if (isinstance(crop, list) and len(crop) == 4
                        and all(isinstance(n, (int, float)) for n in crop)
                        and crop[2] > 0 and crop[3] > 0):
                    ref['crop'] = crop
            assets.append(metadata | {'id': asset_id, 'category': category,
                          'title': metadata.get('title') or path.stem.replace('_', ' ').title(),
                          'model': {'path': key, 'version': facts['version']},
                          'source': self.local_file(source), 'reference': ref,
                          'preview': self.local_file(preview),
                          'thumbnail': self.local_file(thumbnail), 'error': error})
        self.cache = {key: value for key, value in self.cache.items() if key in seen}
        content = {'schema_version': 1, 'assets': assets, 'warnings': warnings}
        revision = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
        return content | {'revision': revision}

    def refresh(self):
        data = self.build()
        write_json(self.root / 'exports/catalog.json', data)
        return data
