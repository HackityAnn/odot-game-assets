# Asset workspace

## Shared implementation

- Style settings: [tools/asset_pack/art_style.py](tools/asset_pack/art_style.py). Change palettes, texture sizes, bevels, preview lights, hex dimensions, and unit conventions there; use those settings from builders and checks.
- Blender helpers: [geometry.py](tools/asset_pack/geometry.py) for meshes/materials/studio, [style_blender.py](tools/asset_pack/style_blender.py) for preview and normal treatment, [painted_finish.py](tools/asset_pack/painted_finish.py) for portable painted maps.
- Create materials with `geometry.material()`; initialize palettes with `geometry.palette()` or `reference_finish.palette()`. Apply `painted_finish.apply(collection, category)` to supported surface materials and `painted_finish.ground(collection, name, category)` to receiving terrain.
- Build shared prototypes once and instance their mesh datablocks. Preserve manual source edits before explicitly rebuilding a library and its dependent models.

## General game style

- Soft painted medieval fantasy on a hex tabletop: chunky readable silhouettes, broad planes, warm wood/plaster, muted stone, and related color shades within surfaces.
- Use Principled BSDF. Keep fine grain, cracks, veins, and worn edges in Base Color, Roughness, and shallow tangent-space Normal maps; use geometry for silhouette and larger joints.
- Use selective two-segment Bevel modifiers; the shared stone bevel is `0.008`. Keep broad planar normals; use Weighted Normal with hardened bevel normals for stone where needed.
- Preserve sharp crystal/armor facets. Smooth organic surfaces selectively with `style_blender.smooth_sides()` or explicit face normals; avoid blanket subdivision or Shade Smooth.
- Pack source images and embed them in GLB. Base Color/Emission images use `sRGB`; Roughness/Normal use `Non-Color`. Default maps are 512 px; crystals and receiving ground use 1024 px.
- Paint restrained, feathered contact shading and local colored bounce onto receiving surfaces. Keep strong directional light out of Base Color; avoid hard floating light/shadow disks.
- Concentrate Emission on runes, luminous undersides, windows, and narrow crystal highlights; retain shaded colored bodies.
- Preview through `geometry.studio()` / `style_blender.preview()`: Cycles, denoising, 1200 × 1200, 64 samples, AgX / Medium High Contrast, large Area Lights, subtle compositor Fog Glow. Preview glow needs an equivalent game-renderer effect.

## Buildings

- Emphasize each role with a readable sign or signature object, substantial timber joints, layered roofs, recessed entrances, and coherent masonry courses.
- Reuse village-kit shingles, props, and architectural helpers; align wood grain with timber length and keep roof/plaster variation subtle.
- Use warmer window centers and restrained amber bounce. Keep extra surface marks subordinate to the main structure.
- Put the building root at ground zero, facing `-Y`. Keep display terrain, studio lights, and atmosphere in separate presentation collections.

## Units

- Keep chibi proportions, readable faces/hands, clear weapons, and distinct faction/role colors. Round skin/gloves selectively while retaining readable cloth and armor planes.
- Reuse the shared 19-bone skeleton, ground-zero root, and `-Y` forward convention. Use `weapon_socket.L/R` for removable equipment; used weapon sockets are non-deforming, anatomical attachment bones remain deforming.
- Keep equipment grip pivots and authored attachment scale. Do not apply the armature modifier when preparing an export.
- Use the shared 24 FPS clips: `idle`, `walk`, `run`, `attack`, `hit`, `death`; the first three loop, locomotion stays in place. Clip lengths come from `art_style.CLIP_FRAMES`.

## Environment

- Reuse forest-kit components and shared mesh data. Vary foliage size, rotation, curvature, and overlap; group fine grass/moss around contacts instead of evenly spaced borders.
- Keep crystal facet normals flat, mushroom caps/stems smooth, and leaf roots darker than their tips. Keep runes on stone surfaces and delicate marks in texture maps.
- Preserve the flat-top hex: radius `2.55`, surface `Z = 0`, bottom `Z = -0.36`; derive neighbor spacing from `art_style.HEX` rather than duplicating numbers.
- Match river north/south endpoints, channel width, and water height. Keep all geometry within the shared footprint and each tile root at the origin.

## Checks and navigation

- Run `mise run check` for fast unit tests and `mise run style-tests` for Blender fixture tests. Run `mise run asset-style-check -- <asset IDs>` to inspect existing sources; `--all` checks the catalog.
- Check GLB geometry/materials with `mise run asset-check -- <asset IDs>`. Use the README's forest and painted-texture checks for grid/library freshness and embedded texture-channel coverage.
- Tests enforce mechanical contracts. Review actual renders/reference images for softness, color balance, silhouettes, and detail density; those remain art judgments.
- Build, check, cache, and worker commands: [README.md — Asset development checks](README.md#asset-development-checks).
- Art references and shared components: [README.md — Reference asset set](README.md#reference-asset-set).
- Catalog metadata and export selection: [catalog/SCHEMA.md](catalog/SCHEMA.md).
- Keep GUI Blender for review; run builds and tests in isolated workers. Check commands export existing sources and never regenerate their geometry.
- Tool discovery should return names first; load one relevant schema. Print one result representation and short log tails. Full Blender logs are in `.cache/asset-check/logs/`.
