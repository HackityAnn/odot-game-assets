"""Tracked Blender jobs with full local logs and bounded terminal output."""
import os
import shutil
import subprocess
import time
from pathlib import Path


def resolve_blender(requested=None):
    if requested:
        return requested
    if os.environ.get('BLENDER'):
        return os.environ['BLENDER']
    if found := shutil.which('blender'):
        return found
    local = Path.home() / '.local/opt/blender-5.2.2-linux-x64/blender'
    return str(local) if local.is_file() else 'blender'


def run_blender(script, args=(), *, blender=None, root, label):
    root = Path(root)
    directory = root / '.cache/asset-check/logs'
    directory.mkdir(parents=True, exist_ok=True)
    log = directory / (label + '.log')
    command = [resolve_blender(blender), '-b', '--factory-startup', '--python-exit-code', '1',
               '--python', str(root / script), '--', *map(str, args)]
    started = time.monotonic()
    print(f'{label}: running (log: {log.relative_to(root)})', flush=True)
    with log.open('w') as stream:
        try:
            subprocess.run(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT, check=True)
        except (OSError, subprocess.CalledProcessError) as error:
            stream.flush()
            tail = '\n'.join(log.read_text(errors='replace').splitlines()[-20:])
            raise RuntimeError(f'{label} failed; full log: {log}\n{tail}') from error
    elapsed = round(time.monotonic() - started, 2)
    print(f'{label}: passed in {elapsed:.2f}s', flush=True)
    return {'job': label, 'seconds': elapsed, 'log': log.relative_to(root).as_posix()}


if __name__=='__main__':
    import argparse
    import sys
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('script')
    parser.add_argument('--blender')
    parser.add_argument('--label',default='blender-tests')
    options,arguments=parser.parse_known_args()
    try:
        run_blender(options.script,arguments,blender=options.blender,
                    root=Path(__file__).resolve().parents[2],label=options.label)
    except RuntimeError as error:
        print(str(error),file=sys.stderr)
        sys.exit(1)
