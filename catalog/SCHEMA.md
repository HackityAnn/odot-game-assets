# Catalog associations, version 1

`catalog/associations.json` is tracked, human-editable metadata. The catalog's
generated index at `exports/catalog.json` is disposable and should not be edited.
Every exported GLB appears without an association. No external reference image
is inferred from an export filename or from a pack-wide reference path.

```json
{
  "schema_version": 1,
  "assets": {
    "exports/props/kit/roof_tile.glb": {
      "title": "Roof tile",
      "source": "sources/props/shared_village_kit.blend",
      "reference": {
        "path": "sources/reference/my_sheet.png",
        "crop": [100, 40, 320, 250]
      },
      "preview": "exports/previews/roof_tile.png",
      "thumbnail": "exports/thumbnails/props/kit/roof_tile.png",
      "animation_policy": {"settle": false, "turn": true}
    }
  }
}
```

All paths are relative to the repository root. Missing files are unavailable
until they exist. Paths outside the repository are rejected. The fields are optional:

| Field | Meaning |
| --- | --- |
| `title` | Display name; otherwise manifest title or a readable export stem |
| `source` | Editable `.blend`; default is the matching relative path in `sources/` |
| `reference` | Object with `path` and optional `[x, y, width, height]` pixel crop; a string path also works |
| `preview` | Rendered image; legacy manifest assets default to `exports/previews/<stem>.png` |
| `thumbnail` | Grid thumbnail; default `exports/thumbnails/<asset-id>.png` |
| `animation_policy` | Clip names mapped to `true` (loop) or `false` (one shot) |
| `export_collection` | Explicit Blender collection to export, for terrain or shared libraries |
| `export_object` | Explicit Blender root object to export with its descendants |

Use `null` to suppress a default source, preview, thumbnail, or reference. Reference
crops use the image's natural pixel dimensions. Without a crop, the full image is
shown. Associations for missing exports are retained but do not create cards.
Export selectors are optional and mutually exclusive. Without one, the exporter
uses a collection or root object matching the asset ID's final segment. Root-level
overview `.blend` files are excluded from batch export. Shared libraries use
explicit per-asset `source` mappings and selectors; no entire library is exported
as a single model implicitly.

The export manifest at `exports/asset_manifest.json` may provide these same fields
on entries in its `assets` array, keyed by `file`. Explicit associations override
them. Export byte size, triangle count, material count, clip names, and available
clip durations come from the GLB itself; they cannot be overridden by prose or
stale counts in a manifest. Triangle totals count mesh primitives (triangle lists,
strips, and fans), matching the existing pack's geometry statistics, rather than
duplicating counts for instances. Materials count material definitions.

Clip loop policy is chosen in this order: association `animation_policy`, per-asset
manifest `animation_policy`, GLB animation `extras.loop` boolean, then manifest
`one_shot_clips` / `looping_clips` defaults for that manifest's listed assets only.
Unknown policy remains `null` in the index; the UI starts with Loop unchecked.
The viewer always discovers playable clips from the actually loaded GLB.

The generated index includes `schema_version`, `revision`, `warnings`, and `assets`.
Each asset has a stable `id` (export-relative path without extension), `category`,
display metadata, statistics, `animations` with `{name, duration, loop}`, and
available `model`, `source`, `reference`, `preview`, and `thumbnail` records.
File records contain repository-relative `path` and cache `version`. The model
version is a SHA-256 hash of the whole GLB; ancillary versions track file changes.
`error` records a model inspection failure while preserving the card.
