"""Explicit incremental thumbnail generation in isolated Blender processes."""
import hashlib
import subprocess
from pathlib import Path

from .index import CatalogIndex, ROOT, write_json

RENDER_VERSION = 1


def render_thumbnails(asset_ids, blender='blender', force=False, root=ROOT):
    index = CatalogIndex(root)
    data = index.refresh()
    available = {asset['id']: asset for asset in data['assets']}
    unknown = set(asset_ids) - available.keys()
    if unknown:
        raise SystemExit('Unknown asset IDs: ' + ', '.join(sorted(unknown)))
    selected = [available[key] for key in asset_ids] if asset_ids else data['assets']
    state_path = Path(root) / 'exports/thumbnails/state.json'
    previous = index.read_json('exports/thumbnails/state.json', [])
    state = previous if previous.get('renderer_version') == RENDER_VERSION else {'renderer_version': RENDER_VERSION, 'assets': {}}
    count = 0
    for asset in selected:
        if asset['error']:
            print(f"Skip {asset['id']}: {asset['error']}")
            continue
        output = Path(root) / 'exports/thumbnails' / (asset['id'] + '.png')
        record = state['assets'].get(asset['id'], {})
        if (not force and output.exists() and record.get('model') == asset['model']['version']
                and record.get('image') == hashlib.sha256(output.read_bytes()).hexdigest()):
            print(f"Unchanged: {asset['id']}")
            continue
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_name(output.stem + '.rendering.png')
        try:
            subprocess.run([blender, '-b', '--factory-startup', '--python-exit-code', '1',
                            '--python', str(Path(__file__).with_name('render_blender.py')),
                            '--', str(Path(root) / asset['model']['path']), str(temporary)], check=True)
            if not temporary.exists():
                raise RuntimeError(f'Thumbnail was not rendered: {asset["id"]}')
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
        state['assets'][asset['id']] = {'model': asset['model']['version'],
                                      'image': hashlib.sha256(output.read_bytes()).hexdigest()}
        write_json(state_path, state)
        print(f"Rendered: {asset['id']}")
        count += 1
    index.refresh()
    print(f'{count} thumbnails rendered')
