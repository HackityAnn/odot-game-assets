"""Create a portable local review gallery from the actual Blender renders and GLBs."""
import json
import shutil
import zipfile
from pathlib import Path
from catalog import ASSETS

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'.lavish'

HTML=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fantasy Village · Blender Asset Review</title>
<script type="module" src="vendor/model-viewer.min.js"></script>
<style>
:root{color-scheme:dark;--bg:#262724;--panel:#333530;--ink:#eee7d7;--muted:#c0b7a6;--line:#606353;--accent:#bdcb83}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,sans-serif}
main{max-width:1440px;margin:auto;padding:42px 32px 60px}h1,h2,h3{font-family:Georgia,serif;font-weight:normal;line-height:1.2}h1{font-size:clamp(36px,5vw,64px);margin:12px 0}h2{font-size:29px;margin:36px 0 18px}h3{font-size:24px;margin:0}
p{max-width:78ch}.eyebrow{color:var(--accent);font-size:12px;letter-spacing:.18em;text-transform:uppercase}.intro{color:var(--muted);max-width:70ch}a{color:var(--accent);text-underline-offset:4px}
.top{display:flex;align-items:start;justify-content:space-between;gap:24px}.top>*{min-width:0}.tools{display:flex;gap:10px;flex-wrap:wrap;margin:22px 0}.button,button,select{border:1px solid var(--line);color:var(--ink);background:var(--panel);border-radius:6px;padding:9px 15px;font:inherit;text-decoration:none;cursor:pointer}button:hover,.button:hover{border-color:var(--accent);background:#414537}button:focus-visible,a:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid var(--accent);outline-offset:3px}.primary{background:var(--accent);color:#22291c;border-color:var(--accent)}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px}.characters{grid-template-columns:repeat(4,minmax(0,1fr))}.card{min-width:0;background:var(--panel);border:1px solid var(--line);border-radius:9px;overflow:hidden}.card button{padding:0;display:block;width:100%;border:0;border-radius:0;text-align:left}.card img{width:100%;display:block;aspect-ratio:1;object-fit:cover}.caption{padding:18px 19px}.caption p{color:var(--muted);font-size:13px;margin:8px 0 0}.tag{font-size:11px;color:var(--accent);letter-spacing:.09em;text-transform:uppercase}.card-links{display:flex;gap:16px;padding:0 19px 16px;font-size:13px}
.strip{display:flex;flex-wrap:wrap;gap:12px;margin-top:20px;color:var(--muted);font-size:13px}.strip span{border:1px solid var(--line);border-radius:99px;padding:5px 12px}.overview{width:100%;display:block;border:1px solid var(--line);border-radius:9px}.notes{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px;margin:30px 0}.notes>*{min-width:0}.notes p{color:var(--muted);font-size:14px;margin-top:9px}.notes h3{font-size:21px}details{border-top:1px solid var(--line);padding:18px 0}summary{cursor:pointer;color:var(--accent)}.reference{width:100%;max-width:1100px;display:block;margin:20px auto}
dialog{width:min(1200px,94vw);max-height:94vh;padding:25px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);overflow:auto}dialog::backdrop{background:#000a}.dialog-head{display:flex;justify-content:space-between;align-items:center;gap:15px}.dialog-head>*{min-width:0}.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}.tabs button[aria-pressed=true]{background:var(--accent);color:#22291c}.compare{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.compare>*{min-width:0}.compare img,.compare svg{width:100%;display:block;aspect-ratio:1;object-fit:contain;background:#333430;border-radius:6px}.label{margin:0 0 9px;color:var(--muted);font-size:13px;text-transform:uppercase;letter-spacing:.1em}model-viewer{display:block;width:100%;height:500px;max-height:65vh;border:1px solid var(--line);border-radius:8px;background:#343731}#model-error{color:#edbf81}#model-controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:12px 0}.meta{color:var(--muted);font-size:13px;overflow-wrap:anywhere}.feedback{margin-top:24px;border-top:1px solid var(--line);padding-top:18px}textarea{width:100%;padding:12px;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;font:inherit;resize:vertical}label{display:block;margin-bottom:8px}.feedback small{display:block;color:var(--muted);margin:8px 0}#queued{color:var(--accent)}[hidden]{display:none!important}
@media(max-width:1050px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.characters{grid-template-columns:repeat(3,minmax(0,1fr))}.top{display:block}}
@media(max-width:680px){main{padding:24px 16px}.grid,.characters,.notes,.compare{grid-template-columns:minmax(0,1fr)}dialog{padding:16px}.top .tools{margin-top:18px}.dialog-head h2{font-size:24px;margin:0}model-viewer{height:370px}.notes{gap:16px}}
</style></head><body><main>
<header class="top"><div><div class="eyebrow">Original Blender assets · Reference reconstruction</div><h1>A little fantasy village.</h1><p class="intro">Eleven buildings and eight characters from your supplied references. The four evil units are initial models. Open any asset to compare the reference with its render, rotate the exported mesh, or play the character animations.</p></div><div class="tools"><a class="button primary" href="fantasy_village_assets.zip" download>Download asset pack</a><a class="button" href="sources/autobattler.blend" download>Open new set .blend</a></div></header>
<div class="strip"><span>19 editable models</span><span>8 shared rigs · 6 clips each</span><span>Shared prop library · 20 components</span><span>2 separate terrain bases</span><span id="validation-state">Export verification</span></div>
<h2>Buildings</h2><section class="grid" id="buildings" aria-label="Building models"></section>
<h2>Characters</h2><section class="grid characters" id="characters" aria-label="Character models"></section>
<h2>The new evil units · Initial models</h2><img class="overview" src="renders/evil_overview.png" alt="Four initial evil unit models in Blender"><p><a href="sources/evil_autobattler.blend" download>Open evil unit overview .blend</a></p><h2>The autobattler village</h2><img class="overview" src="renders/autobattler_overview.png" alt="Seven new buildings and the dual-axe berserker assembled in Blender"><h2>The original set</h2><img class="overview" src="renders/overview.png" alt="All four original buildings and three characters assembled in Blender on separate hex terrain bases">
<section class="notes"><div><h3>Made for the rebuild</h3><p>Your supplied references drive the shapes, colors, and costumes. Sources and exports are independent of the existing game.</p></div><div><h3>Editable parts</h3><p>Timbers, tiles, branches, costume pieces, and equipment remain separate objects in the Blender sources. Terrain and preview atmosphere have their own collections.</p></div><div><h3>First visual pass</h3><p>These are authored interpretations of a single view. The unseen sides are modeled; the six animation clips are a starter set. Polygon and draw-call optimization remains for the next pass.</p></div></section>
<details><summary>Original reference and export details</summary><img class="reference" src="reference.png" alt="The supplied seven-panel fantasy village reference"><p class="meta">Blender sources use Z up, −Y forward, and ground-contact roots at zero. Portable GLB exports use Y up and +Z forward. Character clips: idle, walk, run, attack, hit, death at 24 fps. The first three loop; locomotion is in place. Props use their grip center as origin. Mine rocks and tree roots extend slightly below ground. Smoke and studio lighting belong to the previews.</p><p><a href="asset_manifest.json">Asset manifest</a> · <a href="validation.json">Round-trip validation</a> · <a href="vendor/LICENSE-model-viewer">3D viewer license</a></p></details>
</main>
<dialog id="detail"><div class="dialog-head"><div><div class="eyebrow" id="asset-kind"></div><h2 id="asset-title" style="margin:7px 0"></h2></div><button id="close" aria-label="Close asset review">Close</button></div>
<div class="tabs" aria-label="Asset view"><button id="compare-tab" aria-pressed="true">Reference & render</button><button id="model-tab" aria-pressed="false">Rotate model / animations</button></div>
<div id="compare" class="compare"><div><p class="label">Your reference</p><svg id="reference-crop" role="img" aria-label="Asset in the supplied reference" preserveAspectRatio="xMidYMid meet"><image href="reference.png" width="1536" height="1024"/></svg></div><div><p class="label" id="render-label">Blender render</p><img id="asset-render" alt="Rendered Blender asset"></div></div>
<div id="model-panel" hidden><model-viewer id="viewer" camera-controls touch-action="pan-y" shadow-intensity="1" exposure="1.05" environment-image="neutral" camera-orbit="30deg 68deg auto" alt="Interactive exported 3D asset"></model-viewer><div id="model-controls"><label for="clip" id="clip-label">Animation</label><select id="clip"><option>idle</option><option>walk</option><option>run</option><option>attack</option><option>hit</option><option>death</option></select><button id="play">Play</button><button id="reset-camera">Reset camera</button></div><p id="model-error" hidden></p><p class="meta">Drag to rotate · scroll to zoom · the GLB contains the asset and equipment, with the display terrain exported separately.</p></div>
<p class="meta" id="stats"></p><div class="tools"><a class="button" id="source-link" download>Editable .blend</a><a class="button" id="glb-link" download>Portable .glb</a><a class="button" id="render-link" download>Render .png</a></div>
<form class="feedback" id="feedback" data-lavish-question="asset-feedback"><label for="comment">What would you change on this asset?</label><textarea id="comment" rows="3" placeholder="For example: make the hat wider, shorten the legs, or darken the roof."></textarea><small>Queue your feedback, then use Send to Agent in the Lavish top bar. In a standalone copy, the button copies the feedback.</small><button type="submit">Queue feedback</button><span id="queued" role="status" aria-live="polite"></span></form>
</dialog>
<script>
const assets=__ASSET_DATA__, validation=__VALIDATION__;
let active=null, playing=false;const $=id=>document.getElementById(id), viewer=$('viewer');
$('validation-state').textContent=validation?'GLB round-trip checks passed':'Validation pending';
for(const asset of assets){const card=document.createElement('article');card.className='card';card.id='asset-'+asset.id;card.innerHTML=`<button aria-label="Review ${asset.title}"><img src="renders/${asset.id}.png" alt="Blender render of ${asset.title}" loading="lazy"><div class="caption"><div class="tag">${asset.category==='characters'?'Rigged character':'Building'}</div><h3>${asset.title}</h3><p>${asset.triangles.toLocaleString()} triangles${asset.category==='characters'?' · 6 animation clips':''} · Review asset →</p></div></button><div class="card-links"><a href="sources/${asset.id}.blend" download>.blend</a><a href="models/${asset.id}.glb" download>.glb</a></div>`;card.querySelector('button').onclick=()=>openAsset(asset);$(asset.category).append(card)}
function openAsset(asset){active=asset;$('asset-title').textContent=asset.title;$('asset-kind').textContent=asset.category==='characters'?'Rigged character · Original costume':'Original building';$('asset-render').src='renders/'+asset.id+'.png';$('asset-render').alt='Blender render of '+asset.title;$('reference-crop').setAttribute('viewBox',asset.crop.join(' '));const ref=$('reference-crop').querySelector('image');ref.setAttribute('href',asset.batch==='original'?'reference.png':asset.reference);ref.setAttribute('width',asset.dimensions[0]);ref.setAttribute('height',asset.dimensions[1]);$('render-label').textContent=asset.id==='archer'?'Blender render · bow-draw pose':'Blender render';$('stats').textContent=`${asset.triangles.toLocaleString()} exported triangles · ${asset.materials} materials · ${asset.category==='characters'?'19 bones · 6 starter clips':'editable component meshes'} · Ground origin at zero`;$('source-link').href='sources/'+asset.id+'.blend';$('glb-link').href='models/'+asset.id+'.glb';$('render-link').href='renders/'+asset.id+'.png';$('comment').value='';$('queued').textContent='';$('clip').value='idle';$('clip').hidden=$('clip-label').hidden=$('play').hidden=asset.category!=='characters';$('model-error').hidden=true;viewer.removeAttribute('src');playing=false;$('play').textContent='Play';showTab(false);$('detail').showModal()}
function showTab(model){$('compare').hidden=model;$('model-panel').hidden=!model;$('compare-tab').setAttribute('aria-pressed',String(!model));$('model-tab').setAttribute('aria-pressed',String(model));if(model&&active&&!viewer.getAttribute('src')){viewer.setAttribute('src','models/'+active.id+'.glb');viewer.animationName='idle'}}
$('compare-tab').onclick=()=>{viewer.pause?.();playing=false;$('play').textContent='Play';showTab(false)};$('model-tab').onclick=()=>showTab(true);$('close').onclick=()=>$('detail').close();$('detail').addEventListener('close',()=>{viewer.pause?.();viewer.removeAttribute('src')});$('clip').onchange=()=>{viewer.animationName=$('clip').value;viewer.currentTime=0;if(playing)viewer.play()};$('play').onclick=()=>{playing=!playing;playing?viewer.play():viewer.pause();$('play').textContent=playing?'Pause':'Play'};$('reset-camera').onclick=()=>{viewer.cameraOrbit='30deg 68deg auto';viewer.cameraTarget='auto auto auto';viewer.fieldOfView='auto'};viewer.addEventListener('error',()=>{$('model-error').hidden=false;$('model-error').textContent='The 3D viewer could not load. The Blender renders and downloadable source files remain available.'});
$('feedback').onsubmit=async event=>{event.preventDefault();const comment=$('comment').value.trim();if(!comment){$('comment').focus();return}const text=`Revise ${active.title} (${active.id}) in the Blender asset pack: ${comment}`;if(window.lavish?.queuePrompt){await window.lavish.queuePrompt({tag:'asset-review',text,queueKey:'asset-'+active.id,data:{assetId:active.id,comment},element:$('feedback')});$('queued').textContent=' Feedback queued.'}else{try{await navigator.clipboard.writeText(text);$('queued').textContent=' Feedback copied.'}catch{$('queued').textContent=' Copy your feedback and send it in chat.'}}};
</script></body></html>'''


def main():
    manifest=json.loads((ROOT/'exports'/'asset_manifest.json').read_text())
    metadata={Path(a['file']).stem:a for a in manifest['assets']}
    data=[]
    for asset in sorted(ASSETS,key=lambda a:a['batch']=='original'):
        name,title,category,crop=[asset[key] for key in ['id','title','category','crop']]
        info=metadata[name]
        data.append(dict(asset,triangles=info['triangles'],materials=info['materials']))
        for source,folder in [(ROOT/'sources'/category/f'{name}.blend','sources'),
                              (ROOT/'exports'/category/f'{name}.glb','models'),
                              (ROOT/'exports'/'previews'/f'{name}.png','renders')]:
            (OUT/folder).mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,OUT/folder/source.name)
    (OUT/'vendor').mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'scratch'/'model-viewer.min.js',OUT/'vendor'/'model-viewer.min.js')
    shutil.copy2(ROOT/'sources'/'reference'/'fantasy_village.png',OUT/'reference.png')
    shutil.copytree(ROOT/'sources/reference/autobattler',OUT/'autobattler',dirs_exist_ok=True)
    shutil.copy2(ROOT/'sources'/'fantasy_village.blend',OUT/'sources'/'fantasy_village.blend')
    shutil.copy2(ROOT/'sources'/'autobattler.blend',OUT/'sources'/'autobattler.blend')
    shutil.copytree(ROOT/'sources/reference/evil_autobattler',OUT/'evil_autobattler',dirs_exist_ok=True)
    shutil.copy2(ROOT/'sources/evil_autobattler.blend',OUT/'sources/evil_autobattler.blend')
    shutil.copy2(ROOT/'exports/previews/evil_overview.png',OUT/'renders/evil_overview.png')
    shutil.copy2(ROOT/'exports/previews/autobattler_overview.png',OUT/'renders/autobattler_overview.png')
    shutil.copy2(ROOT/'exports'/'previews'/'overview.png',OUT/'renders'/'overview.png')
    shutil.copy2(ROOT/'exports'/'asset_manifest.json',OUT/'asset_manifest.json')
    validation=ROOT/'exports'/'validation.json'
    if validation.exists(): shutil.copy2(validation,OUT/'validation.json')
    checked={a['asset'] for a in json.loads(validation.read_text())} if validation.exists() else set()
    passed=all(a['id'] in checked for a in ASSETS)
    html=HTML.replace('__ASSET_DATA__',json.dumps(data)).replace('__VALIDATION__','true' if passed else 'false')
    (OUT/'asset-gallery.html').write_text(html)
    with zipfile.ZipFile(OUT/'fantasy_village_assets.zip','w',zipfile.ZIP_DEFLATED) as bundle:
        for folder in ['sources','exports','tools/asset_pack','tools/asset_catalog','catalog']:
            for path in (ROOT/folder).rglob('*'):
                if path.is_file() and path.suffix not in ['.blend1','.pyc'] and '__pycache__' not in path.parts:
                    bundle.write(path,path.relative_to(ROOT))
        bundle.write(ROOT/'README.md','README.md')
    print(OUT/'asset-gallery.html')


if __name__=='__main__': main()
