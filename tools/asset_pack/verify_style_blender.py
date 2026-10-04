"""Check selected existing sources against the shared style; never save or rebuild."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import art_style as style
from style_validation import asset_violations, preview_violations
from tools.asset_catalog.blender_selection import load_asset
from tools.asset_catalog.export_sources import plan_exports
from tools.asset_pack.catalog import BY_ID


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('assets', nargs='*')
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if not args.assets and not args.all:
        parser.error('Supply asset IDs or --all')
    ids = [BY_ID[name]['category'] + '/' + name if name in BY_ID else name for name in args.assets]
    failures = [];count = 0
    for job in plan_exports(ROOT, None if args.all else ids):
        objects = load_asset(job, ROOT)
        painted = any(col.get('modeling_stage') == style.PAINTED_VERSION
                      for obj in objects for col in obj.users_collection)
        errors = asset_violations(objects, Path(job['id']).parts[0], painted=painted, scene=bpy.context.scene)
        # Libraries and earlier models keep their authored presentation until rebuilt.
        if painted and Path(job['source']).stem == Path(job['id']).name:
            errors.extend(preview_violations(bpy.context.scene))
        failures.extend(job['id'] + ': ' + error for error in errors)
        count += 1
        print(('Failed' if errors else 'Verified') + ' art style: ' + job['id'], flush=True)
    if failures:
        raise RuntimeError('\n'.join(failures))
    print('Art style checks passed:', count, 'authored assets')


if __name__ == '__main__':
    main()
