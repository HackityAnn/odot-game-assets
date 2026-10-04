"""Render authored presentation scenes in a worker without saving sources."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import geometry as g
import art_style as style
from catalog import BY_ID


def main(names):
    for name in names:
        asset=BY_ID[name]
        bpy.ops.wm.open_mainfile(filepath=str(g.ROOT/'sources'/asset['category']/f'{name}.blend'))
        scene=bpy.context.scene
        # Bound CPU use when several isolated review renders run concurrently.
        scene.render.threads_mode='FIXED';scene.render.threads=style.PREVIEW.threads
        if not scene.camera:raise ValueError(name+': no presentation camera')
        scene.render.filepath=str(g.ROOT/'exports/previews'/f'{name}.png')
        bpy.ops.render.render(write_still=True)
        print('Rendered preview:',name,flush=True)


if __name__=='__main__':
    main(sys.argv[sys.argv.index('--')+1:])
