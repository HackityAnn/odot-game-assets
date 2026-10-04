"""Compare the building upgrade with its saved first-pass renders and references."""
import html
import shutil
from pathlib import Path

from tools.asset_pack.catalog import ASSETS, ROOT


NOTES = {
    'bakery': 'Larger raised bread sign and counter loaves; heavier roof joints and a recessed oven.',
    'woodcutter_hut': 'Broad axe blade and log emblem; a deeper timber frame and projecting roof joints.',
    'gold_mine': 'Large ore chunks and lintel emblem; deep portal beams and projecting capitals.',
    'tree_house': 'Larger tree banner; stronger balcony supports, room posts and railings.',
    'arrow_tower': 'Larger arrow banner, lookout arrows and target; thicker posts, braces and roof tiers.',
    'bombarding_tower': 'Oversized hollow cannon with a thick muzzle; broad carriage and larger banner.',
    'barracks': 'Large raised sword shield and banner; recessed entrance and substantial arch stones.',
    'stone_cutter': 'Larger grinding wheel and suspended quarry block; a recessed workshop opening.',
    'tavern': 'Larger foaming mug sign and table tankards; a supported sign bracket and deeper entrance.',
    'trade_market': 'Larger scale sign and working balance; broad striped canopy and heavier framing.',
    'magic_academy': 'Larger crystal, orb and arcane banners; solid stepped turret roof and deeper entrance.',
}


def build_review(root=ROOT):
    root=Path(root)
    out=root/'.lavish'
    assets=[a for a in ASSETS if a['category']=='buildings']
    cards=[]
    for asset in assets:
        name=asset['id']; title=html.escape(asset['title'])
        before=root/'.cache/building-upgrade/before'/f'{name}.png'
        for path,folder in [(before,'upgrade/before'),
                            (root/'exports/previews'/f'{name}.png','upgrade/after')]:
            destination=out/folder
            destination.mkdir(parents=True,exist_ok=True)
            shutil.copy2(path,destination/path.name)
        reference='reference.png' if asset['batch']=='original' else asset['reference']
        crop=' '.join(map(str,asset['crop']))
        width,height=asset['dimensions']
        cards.append(f'''<article id="{name}"><header><h2>{title}</h2><p>{NOTES[name]}</p></header>
<div class="compare"><figure><figcaption>Reference</figcaption><svg viewBox="{crop}" role="img" aria-label="{title} reference"><image href="{reference}" width="{width}" height="{height}"/></svg></figure>
<figure><figcaption>First pass</figcaption><img loading="lazy" src="upgrade/before/{name}.png" alt="{title} before upgrade"></figure>
<figure><figcaption>Upgrade</figcaption><img loading="lazy" src="upgrade/after/{name}.png" alt="{title} upgraded Blender render"></figure></div>
<div class="links"><a href="sources/{name}.blend" download>Blender source</a><a href="models/{name}.glb" download>GLB model</a><a href="asset-gallery.html">3D gallery</a></div>
<form data-lavish-question="feedback-{name}" data-asset="{name}"><label for="feedback-{name}">Feedback for {title}</label><textarea id="feedback-{name}" rows="2" placeholder="What should change?"></textarea><button type="submit">Queue feedback</button><span role="status"></span></form></article>''')
    navigation=''.join(f'<a href="#{a["id"]}">{html.escape(a["title"])}</a>' for a in assets)
    document='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Building upgrades · Reference comparison</title><style>
:root{color-scheme:dark;--bg:#262724;--panel:#333530;--ink:#eee7d7;--muted:#c0b7a6;--line:#606353;--accent:#bdcb83}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:40px 24px}h1,h2{font-family:Georgia,serif;font-weight:normal;line-height:1.2}h1{font-size:clamp(32px,5vw,58px);margin:12px 0}h2{font-size:30px;margin:0}p{color:var(--muted);max-width:85ch}.eyebrow{color:var(--accent);letter-spacing:.15em;text-transform:uppercase;font-size:12px}nav,.links{display:flex;flex-wrap:wrap;gap:12px;margin:22px 0}a{color:var(--accent);text-underline-offset:4px}nav a{border:1px solid var(--line);border-radius:6px;padding:5px 10px;font-size:13px}article{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:22px;margin-top:28px;scroll-margin-top:20px;overflow:hidden}article header p{margin:10px 0 20px}.compare{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.compare>*{min-width:0}figure{margin:0}figcaption{color:var(--muted);font-size:12px;letter-spacing:.1em;text-transform:uppercase;margin:0 0 8px}figure:last-child figcaption{color:var(--accent)}img,svg{width:100%;aspect-ratio:1;object-fit:contain;background:#30322e;border-radius:6px;display:block}.links{font-size:14px}form{border-top:1px solid var(--line);padding-top:16px}label{display:block;font-size:14px}textarea{display:block;width:100%;resize:vertical;margin:8px 0 12px;padding:12px;background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:6px;font:inherit}button{background:var(--accent);color:var(--bg);border:0;border-radius:6px;padding:8px 14px;font:inherit;cursor:pointer}form span{margin-left:12px;color:var(--accent);font-size:13px}:focus-visible{outline:3px solid var(--accent);outline-offset:3px}@media(max-width:700px){main{padding:24px 12px}.compare{grid-template-columns:minmax(0,1fr)}article{padding:16px}}
</style></head><body><main><div class="eyebrow">Blender building refinement · 11 assets</div><h1>Bigger identity. Stronger structure.</h1><p>Compare the supplied references, the first pass, and the upgraded models. Signs and signature objects are larger; projecting joints, layered roofs and recessed entrances add depth with broad, readable shapes.</p><p><a href="asset-gallery.html">Open the complete 3D gallery</a> · <a href="fantasy_village_assets.zip" download>Download the asset pack</a></p><nav>__NAV__</nav>__CARDS__</main><script>
for(const form of document.querySelectorAll('form'))form.onsubmit=async event=>{event.preventDefault();const comment=form.querySelector('textarea').value.trim();if(!comment)return;const text='Refine building '+form.dataset.asset+': '+comment;const status=form.querySelector('[role=status]');if(window.lavish?.queuePrompt){await window.lavish.queuePrompt({tag:'building-upgrade',text,queueKey:form.dataset.asset,data:{assetId:form.dataset.asset,comment},element:form});status.textContent='Queued. Use Send to Agent to submit.'}else{try{await navigator.clipboard.writeText(text);status.textContent='Copied. Paste into chat.'}catch{status.textContent='Send your feedback in chat.'}}};
</script></body></html>'''.replace('__NAV__',navigation).replace('__CARDS__','\n'.join(cards))
    path=out/'building-upgrade.html'
    path.write_text(document)
    return path


if __name__=='__main__':
    print(build_review())
