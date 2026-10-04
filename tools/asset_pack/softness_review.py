"""Build a reference/before/finish review using preserved real Blender renders."""
import html
import json
import shutil
from pathlib import Path

from tools.asset_pack.catalog import ASSETS, ROOT


def build_review(root=ROOT):
    root=Path(root);out=root/'.lavish';cards=[]
    assets=[a for a in ASSETS if a['batch'] in ('more_buildings','magical_forest')]
    assets.sort(key=lambda a:a['id']!='hex_crystal_grove')
    audit=root/'.cache/softness/texture-validation.json'
    verified=len(json.loads(audit.read_text())) if audit.exists() else 0
    for asset in assets:
        name=asset['id'];title=html.escape(asset['title'])
        for source,folder in [(root/'.cache/softness/before/exports/previews'/f'{name}.png','before'),
                              (root/'exports/previews'/f'{name}.png','after'),
                              (root/'sources/reference'/asset['reference'],'reference')]:
            target=out/'softness'/folder/f'{name}.png'
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        crop=' '.join(map(str,asset['crop']));width,height=asset['dimensions']
        note=('Sharp crystal facets, cyan/blue/violet surface gradients, thin painted highlights, smoother '
              'mushrooms, curved leaves, fine grass and feathered ground shading.' if asset['category']=='environment'
              else 'Subtle wood grain, plaster and masonry variation, roof gradients, fine normal detail '
              'and warmer window shading. The building silhouette and role details are retained.')
        cards.append(f'''<details id="{name}" {'open' if name=='hex_crystal_grove' else ''}>
<summary>{title}</summary><p class="note">{note}</p><div class="compare">
<figure><figcaption>Reference</figcaption><svg viewBox="{crop}" role="img" aria-label="{title} reference"><image href="softness/reference/{name}.png" width="{width}" height="{height}"/></svg></figure>
<figure><figcaption>Before</figcaption><img src="softness/before/{name}.png" loading="lazy" alt="{title} previous Blender render"></figure>
<figure><figcaption>Painted finish</figcaption><img src="softness/after/{name}.png" loading="lazy" alt="{title} finished Blender render"></figure>
</div><p class="links"><a href="sources/{name}.blend" download>Editable Blender source</a> · <a href="models/{name}.glb" download>GLB model</a> · <a href="softness/after/{name}.png" download>Render</a></p></details>''')
    navigation=''.join(f'<a href="#{a["id"]}">{html.escape(a["title"])}</a>' for a in assets)
    document='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Painted softness · Blender asset review</title><style>
:root{color-scheme:dark;--bg:#262724;--panel:#333530;--ink:#eee7d7;--muted:#c0b7a6;--line:#606353;--accent:#bdcb83}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,sans-serif}main{max-width:1600px;margin:auto;padding:38px 28px 70px}h1,h2,h3,summary{font-family:Georgia,serif;font-weight:normal;line-height:1.2}h1{font-size:clamp(36px,5vw,60px);margin:12px 0 20px}h2{font-size:27px}p{max-width:90ch}.eyebrow{color:var(--accent);font-size:12px;letter-spacing:.18em;text-transform:uppercase}.intro,.note{color:var(--muted)}a{color:var(--accent);text-underline-offset:4px;overflow-wrap:anywhere}nav{display:flex;flex-wrap:wrap;gap:9px;margin:26px 0}nav a{border:1px solid var(--line);border-radius:99px;padding:5px 12px;font-size:13px;text-decoration:none}.compare{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.compare>*{min-width:0}figure{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden}figure img,figure svg{width:100%;display:block;aspect-ratio:1;object-fit:contain}figcaption{padding:12px 15px;font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.09em}details{padding:23px 0;border-top:1px solid var(--line);scroll-margin-top:20px}summary{font-size:28px;cursor:pointer;color:var(--ink)}.changes{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin:30px 0}.changes>*{min-width:0;background:var(--panel);padding:20px;border:1px solid var(--line);border-radius:8px}.changes h2{margin:0}.changes p{font-size:14px;color:var(--muted);margin-bottom:0}.status{color:var(--accent)}.links{font-size:14px}a:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:4px}@media(max-width:850px){main{padding:25px 16px}.compare,.changes{grid-template-columns:minmax(0,1fr)}summary{font-size:25px}}
</style></head><body><main><div class="eyebrow">Fantasy village · Material refinement</div><h1>Sharp shapes, softer surfaces.</h1>
<p class="intro">The new five buildings, eight forest tiles and 25 reusable forest components now carry a shared painted finish. These are actual Blender renders of the preserved previous sources and the updated sources, alongside the supplied references.</p>
<p class="status">__VERIFIED__ assets checked for packed maps, finite UVs and matching embedded GLB texture channels.</p>
<p><a href="asset-gallery.html">Open the complete 3D gallery</a> · <a href="fantasy_village_assets.zip" download>Download asset pack</a></p>
<div class="changes"><section><h2>Material detail</h2><p>Base Color gradients, fine grain and cracks, Roughness variation and subtle tangent Normal maps. Images are 512 px, with 1024 px crystal and ground maps. Source images are packed; GLB images are embedded.</p></section><section><h2>Portable painted light</h2><p>Ground textures blend restrained contact shading and local cyan/amber bounce. Crystal emission is concentrated on narrow highlights so colored body shading remains visible. These cues travel with the assets.</p></section><section><h2>Geometry and presentation</h2><p>Selective stone bevels, curved varied leaves, smooth mushroom caps and fine grass keep the existing style. Larger Area Lights soften render shadows. Compositor Fog Glow is a preview effect; the game can use emission maps for bloom.</p></section></div>
<nav aria-label="Asset comparisons">__NAV__</nav>__CARDS__
<p class="note">The gallery's earth-toned colors and typography are reused here. Reference images are untouched. The hex footprint, origin and river connection conventions are preserved.</p>
</main></body></html>'''
    document=document.replace('__VERIFIED__',str(verified)).replace('__NAV__',navigation).replace('__CARDS__','\n'.join(cards))
    path=out/'material-softness.html';path.write_text(document)
    return path


if __name__=='__main__':
    print(build_review())
