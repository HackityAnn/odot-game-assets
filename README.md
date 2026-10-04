# Odot game assets

Blender asset workspace with [MCP for Blender](https://github.com/ahujasid/mcp-for-blender).

## Local asset catalog

From the repository root, start the permanent catalog with Python 3.11+:

```sh
mise run catalog
```

Without mise, use `python3 -m tools.asset_catalog serve` instead.

Open **http://127.0.0.1:8000** (`--port 8001` selects another port). No npm
install, CDN, AI service, Lavish, or game checkout is required. The viewer and
compression decoders are bundled in `catalog/vendor/`. Stop with Ctrl-C.

Search by asset name or path, select any discovered category, or filter to animated
assets. Opening a card loads its GLB on demand, with orbit, zoom, reset camera,
reference, rendered preview, file statistics, and downloads for available sources.
Animation choices come from the loaded model. Select a clip, play/pause, choose
speed, scrub the timeline (which pauses playback), and override Loop as needed.
One-shot clips hold their last frame. Clips without loop metadata default to one
shot. Search, filters, and the selected asset are preserved in the URL, for example
`http://127.0.0.1:8000/?category=characters&animated=1&asset=characters%2Fknight`.

The browser polls every two seconds. Changed exports, metadata, sources, references,
and previews refresh without restarting the server. Only changed GLBs are parsed;
unchanged open models and grid thumbnails stay loaded. Model URLs include a content
hash to bypass the viewer's cache. **Refresh index** checks immediately. Neither
browsing nor indexing starts Blender, saves sources, builds geometry, or renders.

To rebuild only the disposable metadata index:

```sh
python3 -m tools.asset_catalog index
```

All GLBs under `exports/` are discovered recursively, including standalone props,
exported components, nested folders, and new categories. Root-level exports use
the `uncategorized` category. `exports/catalog.json` is generated and ignored by
Git. Counts and clip names come from the GLB, even if the manifest is stale.
Missing optional files have placeholders; a corrupt export stays visible with
an error and does not hide the other assets. Files are served on localhost only.

### Refresh exports without rebuilding models

To export selected **existing sources** without saving or modifying their `.blend`
files, building geometry, or rendering previews:

```sh
mise run catalog-export buildings/bakery characters/knight props/sword --blender /path/to/blender
```

Omit the asset IDs to export all authored asset sources. Without mise, use
`python3 -m tools.asset_catalog export --blender /path/to/blender` (optionally adding
the asset IDs). The direct Blender worker invocation also remains available.

The `--blender` option selects your executable. Each source must have an
asset collection or root object matching the asset ID's final segment; descendants
and a character's optional `EQUIPMENT` collection are exported, while presentation
collections are omitted. Explicit source mappings support shared component libraries.
This command writes the requested GLBs, updates their manifest records, and
refreshes the index. Exports are replaced atomically. The original
`tools/asset_pack/export_pack.py` workflow also refreshes the index when it finishes;
that older pack workflow can regenerate standalone component sources. Keep using
the selected-source command for manual refinements. Exports from other tools are
picked up automatically by the running catalog.

### Render thumbnails explicitly

```sh
python3 -m tools.asset_catalog thumbnails --blender /path/to/blender
python3 -m tools.asset_catalog thumbnails props/sword characters/knight --blender /path/to/blender
```

The first command considers all exports; the second selects specific asset IDs.
Only missing or changed thumbnails render. `--force` explicitly rerenders the
selection. A separate background Blender process imports each GLB, fits a neutral
studio camera, and writes `exports/thumbnails/<asset-id>.png`. It never opens or
saves a Blender source. Content hashes in `exports/thumbnails/state.json` track
the rendered export and image; the renderer version tracks changes to the setup.
Thumbnail PNGs can be committed for deployment; their cache state and temporary
render files are ignored by Git. Existing rendered
previews are used in the grid when a thumbnail is absent. Nothing renders just
because you refresh an export or browse the catalog.

### Associate references and optional metadata

Edit the tracked [`catalog/associations.json`](catalog/associations.json). See
[`catalog/SCHEMA.md`](catalog/SCHEMA.md) for the small schema, merge priorities,
and examples. Keys are exact repository-relative export paths. Reference mappings
are explicit; a matching filename alone never associates a reference. The initial
mappings preserve the old gallery's seven reference crops and the existing
autobattler pack's reference associations. Unexported mappings are harmless.

Matching sources default to `sources/<export-relative-path>.blend`; set `source`
to override this for shared component libraries. Set `preview` and `thumbnail` for
custom images, and `animation_policy` for clip-specific loop/one-shot behavior.
Updates appear automatically. Export manifest entries may also carry those fields;
the associations file takes precedence. The pack-wide loop defaults only apply
to assets actually listed in that manifest.

The implementation keeps GLB inspection and merging in `tools/asset_catalog/metadata.py`,
discovery in `index.py`, local serving in `server.py`, explicit Blender operations
in separate scripts, and the static UI in `catalog/`. Run focused tests with:

```sh
python3 -m unittest tools.asset_catalog.test_catalog -v
```

Browser verification results and the optional acceptance script are described in
[`catalog/VERIFICATION.md`](catalog/VERIFICATION.md).

### Build and deploy to GitHub Pages

```sh
mise run catalog-build
```

This creates `dist/catalog/`: a complete static website containing the viewer,
fresh catalog JSON, and referenced GLBs, thumbnails, previews, and reference
images. The static packaging command never invokes Blender or changes assets. Editable `.blend` downloads
are excluded from the deployed site; local browsing retains them. Optional
`--include-sources` includes them for other deployments. Build output is ignored
by Git. URLs work both at a domain root and under `/odot-game-assets/`, without
needing a configurable base path.

Preview the artifact using any static HTTP server:

```sh
python3 -m http.server 8001 --bind 127.0.0.1 --directory dist/catalog
```

Open `http://127.0.0.1:8001/`. The static site reads `catalog.json` instead of the
local discovery API and checks for newly deployed metadata once per minute.
**Check for updates** fetches immediately. Local `mise run catalog` still discovers
arbitrary file changes every two seconds.

The workflow at [`.github/workflows/catalog-pages.yml`](.github/workflows/catalog-pages.yml)
tests and builds pull requests targeting `main`; pushes to `main` and manual runs
on `main` also upload the artifact and deploy it to GitHub Pages. Its build steps are:

1. Checkout (including Git LFS assets) and set up Python 3.11.
2. Install Linux dependencies and restore or download pinned Blender 5.2.2 from
   the official archive, verifying its published SHA-256 checksums.
3. Export authored `.blend` sources into GLBs in an isolated background Blender
   worker, including explicitly mapped components from shared libraries.
4. Restore cached thumbnail images and state, then explicitly render only missing
   or changed thumbnails. The first run initializes the cache.
5. Package the static website, upload the Pages artifact, and deploy on `main`.

The pipeline reads authored geometry from the `.blend` files. It never calls the
procedural `build_pack.py` builders or saves source files. Root-level overview
scenes are excluded. Per-asset `export_collection` or `export_object` metadata
selects terrain and shared components when the default naming convention does
not apply. Existing GLBs without editable sources remain browsable.

Deployment uses
the standard GitHub Pages artifact and environment with OIDC; no custom token,
backend, framework, or generated-output branch is needed. The workflow publishes
models and images only. To enable it:

1. Commit the catalog code, workflow, exported assets, associated reference images,
   and desired thumbnail PNGs. CI only sees committed files; untracked local models
   and ignored thumbnail cache state are not available in a fresh checkout.
2. In the repository's **Settings → Pages**, set **Source** to **GitHub Actions**.
3. Push to `main` or run the **Asset catalog** workflow on `main`. The deployment
   job reports the website URL (normally `https://seraph1nia.github.io/odot-game-assets/`).

You can generate or update thumbnails locally before committing, using the
commands above. CI also has a separate explicit rendering step backed by an
incremental cache, so unchanged GLBs do not rerender their thumbnails. If the cache
is unavailable, that step regenerates the required thumbnails from the exports.
Missing optional images retain their placeholders; invalid exports or malformed
metadata fail the build before a new artifact replaces the last working site.
The builder copies referenced files only, strips local Blender source links by
default, deduplicates shared files, and gives files content hashes so fresh
checkouts produce the same index. Use `--out <directory>` for a different artifact
location; only an output directory previously created by this builder is replaced.

This repository is private. Pages from a private repository requires an eligible
GitHub plan, and a private repository does not by itself make its Pages site
private. [GitHub's Pages availability](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
and [Pages access control](https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site)
describe those constraints. [GitHub's published site size limit](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
is 1 GB; this artifact is currently well below that limit.

Run discovery and static packaging tests together with:

```sh
python3 -m unittest tools.asset_catalog.test_catalog tools.asset_catalog.test_build_site tools.asset_catalog.test_export_sources -v
```

## Reference asset set

Browse [the offline reference library](sources/reference/index.html) for all five
reference sets, full-size images, and matching source/render/export links.
The eight original PNGs from `new_autobattler_assets.zip` are preserved in
`sources/reference/autobattler/`; its manifest records archive and image checksums.

`sources/autobattler.blend` assembles the new arrow tower, bombarding tower,
barracks, magic academy, stone cutter, tavern, trade market, and berserker.
Each has an individual source, GLB export, and preview alongside the original set.
The berserker uses the shared 19-bone skeleton and six starter animation clips,
with a dual-axe attack. The building details and berserker modeling pass are ready
for art review before optimization.

`sources/evil_autobattler.blend` assembles initial models of four evil units:
the skeleton melee fighter, horned mage, hooded crossbowman, and horned berserker.
Their untouched PNG references and archive checksums are in
`sources/reference/evil_autobattler/`. Individual editable sources, renders, and
GLBs sit alongside the existing characters. All four use the shared skeleton and
six starter clips; the crossbow, sword/shield, flame staff, and dual axes are
removable equipment. These evil models are a starting pass for further art review.

`sources/props/shared_village_kit.blend` contains twenty reusable, Asset Browser
collections: barrel, crate, lantern, shrub, pine, stone block, roof tile, target,
spear, arrow, mug, book, parcel, bench, axe, cannonball, open barrel, open crate,
skull, and armor spike. New building copies
share mesh datablocks; both equipped axes share geometry too. Portable kit props
are exported as `exports/props/kit_*.glb`. Edit the kit and rebuild the new set to
propagate changes across the individual files; existing sources remain editable
without requiring a live link to the library.
Skulls reuse one mesh set across evil faces, belt buckles, and display dressing;
armor spikes reuse geometry across helmets and shoulders. Equip helpers preserve
each part's authored scale when attaching it to a bone.

The five images from `more_buildings_assets.zip` are preserved in
`sources/reference/more_buildings/`. They map to `archery_range`,
`research_tower` (the observatory), `metal_mine`, `weaver`, and `town_hall`.
The new buildings reuse the village mesh library and architectural helpers,
with individual editable sources, GLBs, presentation renders, and catalog links.

The eight images from `magical_forest_environment_assets.zip` are preserved in
`sources/reference/magical_forest/`. Each has a matching complete hex tile:
`hex_crystal_grove`, `hex_mystical_grove`, `hex_rune_shrine`,
`hex_glowing_mushrooms`, `hex_lantern_bridge`, `hex_bioluminescent_grove`,
`hex_woodland_bridge`, and `hex_crystal_shrine`. Their terrain is included in the
GLB. Crystals and mushroom undersides use emissive materials; visible glow halos
can be added by the game's renderer. Water is an opaque stylized mesh.

`sources/environment/shared_forest_kit.blend` contains 25 reusable Asset Browser
collections. Crystals, mushrooms, boulders, moss, leaves, ferns, roots, tree
snags, rune shapes, shrine platforms, lantern posts, stone arch wedges,
bridge planks/posts/rails, hex bases, waterfalls, and foam also export as
individual GLBs under `exports/environment/components/forest_*.glb`.
The catalog maps each component to its source collection in the shared library.
`tools/asset_pack/forest_tiles.py` holds the tile compositions; geometry is authored
once in `forest_kit.py`. Repeated instances share mesh datablocks in each source.
Rebuild the library and tiles explicitly to propagate a library edit.

Forest hexes use a flat-top footprint with radius **2.55**, meadow surface
**Z = 0**, and foundation bottom **Z = −0.36** in Blender. Neighbor columns are
**3.825** apart; rows are **4.41672956** apart, with alternate columns offset by
half a row. Both bridge rivers connect the north and south edges with matching
water height and channel width. Individual tile roots retain those dimensions
as custom properties. `verify_forest_blender.py` checks every vertex against
the six tile edges and compares embedded component meshes with the current
library prototypes. The standard asset check also round-trips every tile and
component through GLB and checks repeated mesh sharing.

Build and review the new sets in isolated workers:

```sh
python3 -m tools.asset_pack.worker tools/asset_pack/build_pack.py --label more-buildings archery_range research_tower metal_mine weaver town_hall --no-render
python3 -m tools.asset_pack.worker tools/asset_pack/forest_kit.py --label forest-kit
python3 -m tools.asset_pack.worker tools/asset_pack/forest_tiles.py --label forest-tiles --no-render
mise run asset-check -- archery_range research_tower metal_mine weaver town_hall hex_crystal_grove hex_mystical_grove hex_rune_shrine hex_glowing_mushrooms hex_lantern_bridge hex_bioluminescent_grove hex_woodland_bridge hex_crystal_shrine
python3 -m tools.asset_catalog export environment/components/forest_crystal_blue
python3 -m tools.asset_pack.worker tools/asset_pack/verify_forest_blender.py --label forest-grid-validation
python3 -m tools.asset_pack.worker tools/asset_pack/render_previews.py --label new-previews archery_range research_tower metal_mine weaver town_hall
python3 tools/asset_pack/reference_index.py
```

`forest_tiles.py` with no asset names builds all eight tiles. Pass names to select
a subset. Builders overwrite generated sources; preserve manual refinements first.
`render_previews.py` renders existing presentation scenes without saving sources;
pass forest tile IDs to render them too. Use the catalog thumbnail command for
portable component previews. Both archive manifests retain the original filenames
and checksums; provenance notes record what the supplied archives contain. The new
buildings and forest tiles have a painted material finish: related color gradients
inside facets, fine timber grain, restrained stone cracks, leaf veins and root-to-tip
shading. `painted_finish.py` samples deterministic surface fields directly into
512-pixel image maps (1024 for crystals and receiving ground), with Base Color,
Roughness, tangent Normal and masked Emission inputs on Principled BSDF materials.
This avoids unsupported procedural node networks in GLB exports. PNGs live beside
the source category in `textures/`; each source also packs its images. Shared
prototype-local UVs preserve repeated mesh reuse.

Crystal facets stay sharp, with irregular rings, blue/cyan/violet color washes and
thin painted edge highlights. Mushroom caps are smoother; leaves have varied,
curved silhouettes. Small stone bevels replace raised crack strokes, runes sit on
the monolith's stone face, and fine grass tufts soften ground intersections. Terrain
maps blend soft contact occlusion and local cyan/amber bounce into receiving surfaces,
replacing hard light disks. These authored cues remain visible without scene lights.
Presentation scenes render at 1200 × 1200 with 64 samples, larger Area Lights and
subtle compositor Fog Glow. The halo is presentation-only; a game renderer can use
the exported emission maps for its own bloom. Shared refinements are authored in the
library and propagated to every forest tile.

After the standard asset checks, audit the packed image maps, source UVs and matching
embedded GLB texture channels with:

```sh
python3 -m tools.asset_pack.worker tools/asset_pack/verify_painted_blender.py --label painted-texture-validation buildings/archery_range environment/hex_crystal_grove environment/components/forest_crystal_blue
```

Previous sources, GLBs and renders for this pass are retained locally under
`.cache/softness/before/`; the comparison is in `.lavish/material-softness.html`.
Refresh the gallery, then run `python3 -m tools.asset_pack.softness_review` to
regenerate that comparison from the saved before renders and current previews.

`sources/fantasy_village.blend` assembles four buildings and three characters
modeled from `sources/reference/fantasy_village.png`: tree house, bakery, gold
mine, woodcutter's hut, knight, mage, and archer. This set is independent of the
existing game's asset mappings and animation conventions, for the upcoming rebuild.

Each model has an editable `.blend` in its source category and a matching `.glb`
in `exports/`. Terrain bases and weapons have separate source/export files.
The individual character exports include their equipped props. Sources retain
the component meshes, palette materials, and rigs. Display terrain, smoke, and
studio lighting are separate presentation collections; building and character
exports omit those collections. `exports/previews/` contains the actual renders.

All eleven buildings have a second reference refinement pass: larger role signs
and signature objects, substantial stone courses and timber joints, thicker
roof shingles, and recessed entrances. The bakery emphasizes bread, the barracks
its raised sword shield, the towers arrows and a hollow cannon, and the academy
its crystal and orb. Geometry stays in broad shapes for readability at game scale.
The updated sources, GLBs, previews, and catalog thumbnails use the same asset IDs.
Characters remain at their existing modeling stage.

For a local before/reference/after review, save the previous building previews
under `.cache/building-upgrade/before/` before rebuilding, refresh the asset
gallery, then run `python3 -m tools.asset_pack.building_review`. This writes
`.lavish/building-upgrade.html` using the gallery's source and model downloads.

Characters share a 19-bone skeleton with `weapon_socket.L` and `weapon_socket.R`.
The starter clips are `idle`, `walk`, `run`, `attack`, `hit`, and `death` at 24 fps.
The first three loop; locomotion stays in place. Source coordinates use Z up and
−Y forward; GLB uses Y up and +Z forward. Building/character root pivots are at
ground zero; props are centered on their grips. Mine rocks and tree roots are
partially buried. These are visual interpretations of the single supplied view;
polygon and draw-call optimization can follow art review.

Rebuild with Blender 5.2's Python runner (substitute your Blender executable):

```sh
blender -b --python-exit-code 1 --python tools/asset_pack/village_kit.py
blender -b --python-exit-code 1 --python tools/asset_pack/build_pack.py -- arrow_tower bombarding_tower barracks stone_cutter tavern trade_market magic_academy berserker
blender -b --python-exit-code 1 --python tools/asset_pack/build_pack.py -- evil_melee_unit evil_mage_unit evil_ranged_unit evil_berserker_unit
blender -b --python-exit-code 1 --python tools/asset_pack/build_pack.py -- woodcutter_hut bakery gold_mine tree_house knight mage archer
blender -b --python-exit-code 1 --python tools/asset_pack/export_pack.py
blender -b --python-exit-code 1 --python tools/asset_pack/verify_pack.py
blender -b --python-exit-code 1 --python tools/asset_pack/showcase.py
blender -b --python-exit-code 1 --python tools/asset_pack/showcase.py -- --autobattler
blender -b --python-exit-code 1 --python tools/asset_pack/showcase.py -- --evil
python3 tools/asset_pack/reference_index.py
python3 tools/asset_pack/gallery.py
```

The scripts overwrite this generated set; keep manual refinements separately
before regenerating. The manifest records export geometry/material counts.
Round-trip verification checks reimported bounds, materials, skinning, animation
playback, loop endpoints, and source-versus-GLB animated poses. Validation records
source and export SHA-256 hashes to detect stale results.
The local `.lavish/asset-gallery.html` review surface
also offers a 3D viewer and a downloadable ZIP of the sources, exports, and scripts.

## Asset development checks

The short visual rules are in [AGENTS.md](AGENTS.md). Numeric settings live in
[`tools/asset_pack/art_style.py`](tools/asset_pack/art_style.py), a pure Python
configuration shared by builders, Blender helpers and validators. The base palette
keeps established unit/faction colors; the painted palette carries the building and
forest finish. Mesh helpers use the shared bevel policy; forest builders derive
facets, organic smoothing, UV names and hex dimensions from it; unit builders use
its rounded-material and animation conventions. `geometry.studio()` applies the
common preview preset, and repeated applications preserve light energy and reuse
the compositor. Previously authored source files retain their saved presentation
until an explicit rebuild; style checks never restyle or save them.

The fast style tests run within `mise run check`. `mise run style-tests` creates
temporary Blender fixtures and tests actual node/material application, selective
normals, idempotent lighting, color encoding, packed maps, UVs, shared unit clips,
attachments and a real GLB texture export. `mise run asset-style-check -- <IDs>`
inspects selected existing sources; `--all` checks the catalog. It enforces native
Principled materials, required painted map channels/color spaces, texture sizes,
UVs, shape-specific normal treatment, root/hex conventions, unit sockets and clip/FPS
conventions.
Individual painted assets also check the saved presentation preset; older assets
and shared libraries keep their authored presentation settings. Visual resemblance,
palette balance and silhouette readability still require render/reference review.
CI runs both the fixture tests and catalog style audit after Blender installation.

Run `mise run check` for Python lint, Python and JavaScript syntax, worker safety
checks, and fast unit tests. Ruff is pinned in `requirements-checks.txt`; the local
command uses the installed Python module or `uvx` without installing mise tools.
CI runs the same checks before exporting sources, followed by attachment regression
tests and source-to-GLB verification for models, standalone props, and terrain.

```sh
mise run asset-check -- berserker
mise run asset-check -- evil_melee_unit props/kit_skull
mise run asset-check -- --all
mise run asset-check -- berserker --force
mise run blender-tests
mise run style-tests
mise run asset-style-check -- archery_range hex_crystal_grove knight
mise run asset-style-check -- --all
```

The incremental check accepts short model names or canonical `category/name` IDs.
It exports only changed authored sources and verifies only stale results. It never
rebuilds geometry, saves a `.blend`, renders, or touches the GUI Blender instance.
Source, export, exporter, verifier, runtime, selection, and shared-kit fingerprints
invalidate cached results. An unchanged verified run starts no Blender workers.
Set `BLENDER` or pass `--blender /path/to/blender` to choose the executable; otherwise
the runner uses PATH or this machine's pinned Blender installation.

Shared kit geometry is embedded in individual models. A kit edit invalidates checks
for dependent models and library exports, but exporting existing sources cannot
propagate that edit into their embedded geometry. The command reports this when it
detects a library change. Rebuild the affected models explicitly using the commands
above after preserving manual edits, then rerun their checks.

Every worker prints a start, finish, duration, and log location. Full logs and job
timings are retained in `.cache/asset-check/`; failures print the final twenty log
lines and return a nonzero exit status. Selected verification merges its records
into `exports/validation.json`, retaining other asset results. File hashes prevent
stale records from being reported as current. The cache is disposable.

Generate the review gallery with `python3 tools/asset_pack/gallery.py`. It copies
the tracked viewer, licenses, and decoder assets from `catalog/vendor/` and works
without `scratch/` or an existing `.lavish/` directory.

For agent tool discovery, list matching tool names before requesting one schema.
Use focused Blender RNA queries and print only the relevant fields of
`structuredContent` or `content`, rather than both. Worker log files provide the
full evidence when a short terminal summary needs investigation.

## Folder layout

`sources/` holds editable originals (`.blend`, layered artwork, audio projects).
`exports/` holds game-ready files (`.glb`, `.png`, `.svg`, `.wav`, `.ogg`).
Both use the same categories:

| Folder | Assets for The Common Watch |
| --- | --- |
| `buildings/` | Farm, gold mine, lumbermill, barracks, archery range, Arcanum, research tower, arrow tower, catapult tower, stonecutter, metal mine, weaver, market, town hall; home and defender structures |
| `characters/` | Adventurer and skeleton swordsmen, berserkers, crossbowmen and mages, including rigs and animations |
| `environment/` | Grass hexes, slopes, river hexes, bridges, trees, hills and mountains |
| `props/` | Weapons, arrows, resource piles, rocks, barrels, sacks, targets, flags and building upgrade pieces |
| `effects/` | Authored attack, impact and status-effect visuals, if replacing or extending the game's procedural effects |
| `ui/` | Resource, unit and research icons; buttons, panels and health bars |
| `audio/` | Music and sound effects |

For example:

```text
sources/buildings/gold_mine.blend
exports/buildings/gold_mine.glb
sources/characters/adventurer_swordsman.blend
exports/characters/adventurer_swordsman.glb
sources/environment/hex_grass.blend
exports/environment/hex_grass.glb
```

Keep textures beside the asset that uses them; put shared textures in the same
category with a descriptive name such as `village_palette.png`. Add an asset
subfolder only when its supporting files make the category crowded. Use an
ignored `scratch/` folder for disposable experiments and test scenes.

## Naming and game integration

- Use lowercase `snake_case` for folders and filenames, with matching source
  and export stems. Git tracks revisions; avoid names such as `final_v2`.
- Name buildings after their gameplay role: `farm`, `gold_mine`, `lumbermill`,
  `barracks`, `archery_range`, `arcanum`, `research_tower`, `arrow_tower`,
  `catapult_tower`, `stonecutter`, `metal_mine`, `weaver`, `market`, `town_hall`.
  The game calls its gold mine `Building.Mine`; use `gold_mine` here to make
  its purpose clear. The old Blacksmith gameplay role is now Research Tower;
  the current blacksmith model is reused for Stonecutter.
- Prefix characters with their faction and use the gameplay role, for example
  `adventurer_swordsman`, `skeleton_berserker`, `adventurer_crossbowman` and
  `skeleton_mage`. Use explicit weapon names such as `sword_1handed` and
  `axe_2handed` in `props/`.
- Add meaningful variants only when they exist: `hex_river_bend`,
  `town_hall_blue`, or `arrow_tower_level_02`. Building levels do not
  automatically require separate models; the game also uses attached upgrade
  pieces.

These categories come from `../odot-game/src/Game.Core/Catalogs.cs` and the
game's `UnitAssets.cs`, `VillageLandscape.cs` and `Tabletop.cs`. Its current
look is a stylized medieval countryside on a hex tabletop.

Prefer `.glb` for new 3D exports so meshes, materials and textures travel
together. Before integrating a character, check `UnitAssets.cs` for the
required animation names, attack clips and `handslot.r` weapon attachment.
Terrain needs consistent hex footprints and authored origins; buildings and
props need sensible ground-contact pivots.

Finished exports can be copied into `../odot-game/src/Game/Assets/` and wired
into the game's asset mappings. Exporting here does not update the game
automatically. The existing KayKit and TrioUI assets remain in the game repo.
Keep the source URL, author and license beside any third-party asset you bring
in, for example `gold_mine.provenance.md`, and retain its license text.

## Tools

Run `mise install` to install the Python 3.11 and uv versions in `mise.toml`.
The MCP server uses `uvx --python 3.11 mcp-for-blender==2.1.3` and a uv-managed
interpreter, following upstream's Python compatibility recommendation.
No project virtual environment is needed.

## Codex and Blender

This machine has the upstream **MCP for Blender** Codex plugin installed from
`~/.local/share/blender-mcp/mcp-for-blender/integrations/codex` and the add-on
enabled in Blender 5.2. The plugin starts its MCP server and provides the
viewport and asset pickers in supported Codex clients.

1. Restart Codex so it loads the plugin.
2. Open Blender. The add-on starts its socket server automatically on
   `localhost:9876`.
3. In the 3D viewport, press **N**, open **MCP for Blender**, and check that the
   server is running. Click **Start MCP Server** if needed.
4. Ask Codex to inspect the scene or create an asset.

To set up the plugin on another machine:

```sh
git clone https://github.com/ahujasid/mcp-for-blender.git
codex plugin marketplace add ./mcp-for-blender/integrations/codex
codex plugin add mcp-for-blender@mcp-for-blender
uvx --python 3.11 mcp-for-blender==2.1.3 install-addon
```

Enable **Interface: MCP for Blender** in Blender's add-on preferences if it is
not already enabled. For GUI clients that cannot find `uvx`, use its absolute
path in the plugin's `.mcp.json`. To pin the server interpreter there, add
`--python`, `3.11` before the package argument and set
`UV_PYTHON_PREFERENCE` to `only-managed` in its `env` table. This machine's
plugin source already has those settings and pins the server to 2.1.3.

Use `mise run blender-addon-install` to reinstall the add-on; restart Blender
afterward. `mise run blender-mcp` starts a standalone stdio server for manual
use. Let the Codex plugin run the server during normal use.
