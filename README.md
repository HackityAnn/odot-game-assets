# Odot game assets

Blender asset workspace with [MCP for Blender](https://github.com/ahujasid/mcp-for-blender).

## Reference asset set

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

Characters share a 19-bone skeleton with `weapon_socket.L` and `weapon_socket.R`.
The starter clips are `idle`, `walk`, `run`, `attack`, `hit`, and `death` at 24 fps.
The first three loop; locomotion stays in place. Source coordinates use Z up and
−Y forward; GLB uses Y up and +Z forward. Building/character root pivots are at
ground zero; props are centered on their grips. Mine rocks and tree roots are
partially buried. These are visual interpretations of the single supplied view;
polygon and draw-call optimization can follow art review.

Rebuild with Blender 5.2's Python runner (substitute your Blender executable):

```sh
blender -b --python-exit-code 1 --python tools/asset_pack/build_pack.py -- woodcutter_hut bakery gold_mine tree_house knight mage archer
blender -b --python-exit-code 1 --python tools/asset_pack/export_pack.py
blender -b --python-exit-code 1 --python tools/asset_pack/verify_pack.py
blender -b --python-exit-code 1 --python tools/asset_pack/showcase.py
```

The scripts overwrite this generated set; keep manual refinements separately
before regenerating. The manifest records export geometry/material counts.
Round-trip verification checks reimported bounds, materials, skinning, animation
playback, and loop endpoints. The local `.lavish/asset-gallery.html` review surface
also offers a 3D viewer and a downloadable ZIP of the sources, exports, and scripts.

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
