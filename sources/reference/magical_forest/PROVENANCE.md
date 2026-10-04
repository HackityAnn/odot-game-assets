# Magical forest references

Imported without image changes from
`~/Downloads/magical_forest_environment_assets.zip`. The archive contains eight
PNGs and no attribution or license document. `manifest.json` records archive
and image SHA-256 checksums and maps each PNG to its assembled hex tile.

The Blender geometry is authored here from these images. Shared crystals,
mushrooms, rocks, plants, roots, rune markings, shrine pieces, bridge parts,
waterfalls, foam, and hex bases live in
`sources/environment/shared_forest_kit.blend`. All 25 components export separately
under `exports/environment/components/`. Tile recipes embed instances sharing
mesh datablocks, so each individual tile stays editable and portable.
