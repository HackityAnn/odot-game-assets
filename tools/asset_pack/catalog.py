"""Asset IDs, source categories and reference framing shared by the pack tools."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = [
    ('tree_house', 'Tree House', 'buildings', [0, 0, 382, 440]),
    ('bakery', 'Bakery', 'buildings', [383, 0, 384, 440]),
    ('gold_mine', 'Gold Mine', 'buildings', [769, 0, 383, 440]),
    ('woodcutter_hut', 'Woodcutter’s Hut', 'buildings', [1153, 0, 383, 440]),
    ('knight', 'Knight', 'characters', [0, 515, 486, 388]),
    ('mage', 'Mage', 'characters', [488, 515, 499, 388]),
    ('archer', 'Archer', 'characters', [989, 515, 547, 388]),
]
ASSETS = [dict(id=n, title=t, category=c, crop=v,
               reference='fantasy_village.png', dimensions=[1536, 1024], batch='original')
          for n, t, c, v in ORIGINAL]
for batch in ['autobattler','evil_autobattler']:
    manifest=ROOT/'sources/reference'/batch/'manifest.json'
    if not manifest.exists(): continue
    for entry in json.loads(manifest.read_text())['assets']:
        ASSETS.append(dict(id=entry['id'], title=entry['title'], category=entry['category'],
                          crop=entry.get('crop',[0,0,entry['width'],entry['height']]),
                          reference=batch+'/'+entry['image'],
                          dimensions=[entry['width'],entry['height']], batch=batch))
BY_ID = {entry['id']: entry for entry in ASSETS}
BUILDINGS = [entry['id'] for entry in ASSETS if entry['category']=='buildings']
CHARACTERS = [entry['id'] for entry in ASSETS if entry['category']=='characters']
AUTOBATTLER = [entry['id'] for entry in ASSETS if entry['batch']=='autobattler']
EVIL = [entry['id'] for entry in ASSETS if entry['batch']=='evil_autobattler']
NEW = AUTOBATTLER+EVIL
